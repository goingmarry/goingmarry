from typing import Any, Dict

from rest_framework import serializers

from .models import User


class UserCreateSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["user_id", "nickname", "email", "gender"]
        extra_kwargs: Dict[str, Dict[str, Any]] = {
            "password": {"write_only": True},
            "gender": {"required": False},
            "email": {"required": False},
        }

    def create(self, validated_data: Dict[str, Any]) -> User:
        return User.objects.create_user(**validated_data)


class NicknameUpdateSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["nickname"]
