from typing import Any, Dict

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User

# class UserCreateSerializer(serializers.ModelSerializer[User]):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ["user_id", "password", "nickname", "email", "gender"]
#         extra_kwargs = {
#             "gender": {"required": False},
#         }

#     def create(self, validated_data: Dict[str, Any]) -> User:
#         validated_data["password"] = make_password(validated_data.get("password"))
#         return User.objects.create_user(**validated_data)


class NicknameUpdateSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["nickname"]


class VerificationSerializer(serializers.Serializer[Any]):
    verification_code = serializers.CharField(max_length=6)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        user_id = attrs.get("user_id")
        password = attrs.get("password")

        if user_id and password:
            user = authenticate(
                username=user_id, password=password
            )  # username으로 변경

            if not user:
                raise serializers.ValidationError(
                    "No active account found with the given credentials"
                )

            if not user.is_active:
                raise serializers.ValidationError("This account is inactive")

            attrs["username"] = user_id
            return super().validate(attrs)
        else:
            raise serializers.ValidationError('Must include "user_id" and "password".')


class UserCreateSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["user_id", "password", "nickname", "email", "gender"]
        extra_kwargs = {
            "gender": {"required": False},
        }

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data["password"] = make_password(validated_data.get("password"))
        user: User = User.objects.create(**validated_data)
        return user
