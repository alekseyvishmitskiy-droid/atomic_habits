from rest_framework import serializers
from habits.models import Habit
from habits.validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user", "last_sent")
        validators = [HabitValidator()]

    def validate(self, attrs):
        if self.instance:
            full_data = {
                "related_habit": attrs.get("related_habit", self.instance.related_habit),
                "reward": attrs.get("reward", self.instance.reward),
                "duration": attrs.get("duration", self.instance.duration),
                "is_pleasant": attrs.get("is_pleasant", self.instance.is_pleasant),
                "periodicity": attrs.get("periodicity", self.instance.periodicity),
            }
            HabitValidator()(full_data)
        return attrs
