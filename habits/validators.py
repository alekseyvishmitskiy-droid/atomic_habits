from rest_framework.serializers import ValidationError


class HabitValidator:
    def __call__(self, attrs):
        related_habit = attrs.get("related_habit")
        reward = attrs.get("reward")
        duration = attrs.get("duration")
        is_pleasant = attrs.get("is_pleasant")
        periodicity = attrs.get("periodicity")


        if related_habit and reward:
            raise ValidationError(
                "Нельзя одновременно выбрать связанную привычку и указать вознаграждение."
            )


        if duration is not None and duration > 120:
            raise ValidationError(
                "Время выполнения не должно превышать 120 секунд."
            )


        if related_habit and not related_habit.is_pleasant:
            raise ValidationError(
                "В связанные привычки можно добавлять только привычки с признаком приятной привычки."
            )


        if is_pleasant and (reward or related_habit):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )


        if periodicity is not None and (periodicity < 1 or periodicity > 7):
            raise ValidationError(
                "Нельзя выполнять привычку реже, чем 1 раз в 7 дней (значение от 1 до 7)."
            )
