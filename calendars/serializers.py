from typing import Any

from rest_framework import serializers

from .models import Calendar


class CalendarSerializer(serializers.ModelSerializer[Calendar]):
    class Meta:
        model = Calendar
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "is_deleted")
