from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.tasks import send_habit_reminders
from users.models import User


class HabitTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123", tg_chat_id="123456"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time="18:00:00",
            action="Принять ванну с пеной",
            is_pleasant=True,
            duration=60,
        )

        self.useful_habit = Habit.objects.create(
            user=self.user,
            place="На улице",
            time="17:30:00",
            action="Прогулка вокруг квартала",
            is_pleasant=False,
            related_habit=self.pleasant_habit,
            periodicity=1,
            duration=90,
            is_public=True,
        )

    def test_create_habit(self):
        url = reverse("habits-list")
        data = {
            "place": "Офис",
            "time": "09:00:00",
            "action": "Выпить стакан воды",
            "reward": "Съесть яблоко",
            "duration": 30,
            "periodicity": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)

    def test_validator_reward_and_related_habit(self):
        url = reverse("habits-list")
        data = {
            "place": "Дом",
            "time": "10:00:00",
            "action": "Зарядка",
            "reward": "Кофе",
            "related_habit": self.pleasant_habit.id,
            "duration": 60,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_duration(self):
        url = reverse("habits-list")
        data = {
            "place": "Дом",
            "time": "10:00:00",
            "action": "Чтение книги",
            "reward": "Чай",
            "duration": 150,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_related_not_pleasant(self):
        url = reverse("habits-list")
        data = {
            "place": "Дом",
            "time": "10:00:00",
            "action": "Отжимания",
            "related_habit": self.useful_habit.id,
            "duration": 60,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_pleasant_with_reward(self):
        url = reverse("habits-list")
        data = {
            "place": "Дом",
            "time": "10:00:00",
            "action": "Посмотреть сериал",
            "is_pleasant": True,
            "reward": "Шоколадка",
            "duration": 60,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_periodicity(self):
        url = reverse("habits-list")
        data = {
            "place": "Дом",
            "time": "10:00:00",
            "action": "Уборка",
            "reward": "Отдых",
            "duration": 60,
            "periodicity": 8,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_and_public_habits(self):
        response = self.client.get(reverse("habits-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)


        self.client.force_authenticate(user=self.other_user)
        public_response = self.client.get(reverse("public_habits"))
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(public_response.data["count"], 1)

    def test_permission_denied_for_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("habits-detail", args=[self.useful_habit.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("habits.tasks.send_telegram_message")
    @patch("habits.tasks.timezone.localtime")
    def test_send_habit_reminders(self, mock_localtime, mock_send):
        mock_localtime.return_value = self.useful_habit.time
        from datetime import datetime
        from django.utils import timezone

        fixed_dt = timezone.make_aware(datetime(2026, 11, 12, 17, 30, 0))
        mock_localtime.return_value = fixed_dt

        send_habit_reminders()
        mock_send.assert_called_once()

    def test_habit_str_and_patch(self):
        self.assertIn("Прогулка вокруг квартала", str(self.useful_habit))


        url = reverse("habits-detail", args=[self.useful_habit.id])
        response = self.client.patch(url, {"place": "Парк"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["place"], "Парк")

    @patch("habits.services.requests.post")
    def test_send_telegram_message_service(self, mock_post):
        from habits.services import send_telegram_message

        send_telegram_message("123456", "Тестовое сообщение")
        mock_post.assert_called_once()

