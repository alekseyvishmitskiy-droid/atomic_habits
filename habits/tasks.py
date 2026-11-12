from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from habits.models import Habit
from habits.services import send_telegram_message


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    today = now.date()


    habits = Habit.objects.filter(
        is_pleasant=False,
        time__hour=current_time.hour,
        time__minute=current_time.minute,
        user__tg_chat_id__isnull=False,
    ).exclude(user__tg_chat_id="")

    for habit in habits:
        if habit.last_sent is None or (today - habit.last_sent) >= timedelta(days=habit.periodicity):
            reward_text = habit.reward if habit.reward else (
                habit.related_habit.action if habit.related_habit else "отличное настроение"
            )
            message = (
                f"Напоминание о привычке!\n"
                f"Время: {habit.time.strftime('%H:%M')}\n"
                f"Действие: {habit.action}\n"
                f"Место: {habit.place}\n"
                f"Вознаграждение: {reward_text}"
            )
            send_telegram_message(habit.user.tg_chat_id, message)
            habit.last_sent = today
            habit.save(update_fields=["last_sent"])
