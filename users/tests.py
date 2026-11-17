from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserTestCase(APITestCase):
    def test_user_registration_and_login(self):
        register_url = reverse("register")
        register_data = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "tg_chat_id": "987654321",
        }
        response = self.client.post(register_url, register_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        token_url = reverse("token_obtain_pair")
        login_data = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
        }
        token_response = self.client.post(token_url, login_data, format="json")
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
