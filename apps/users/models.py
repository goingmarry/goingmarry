from typing import Any, Optional, cast

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager[Any]):
    def create_user(
        self, user_id: str, password: Optional[str] = None, **extra_fields: Any
    ) -> "User":
        if not user_id:
            raise ValueError("User ID is required")
        user = cast(User, self.model(user_id=user_id, **extra_fields))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, user_id: str, password: Optional[str] = None, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(user_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_num = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    nickname = models.TextField()
    email = models.CharField(max_length=100, unique=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 이메일 & 핸드폰 번호 인증
    phone_number = models.CharField(max_length=15, null=False, default='0000000000')  # 기본값 추가
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_created_at = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["nickname", "email"]

    def __str__(self) -> str:
        return self.user_id
