# user/services.py
from typing import Any, Dict, Optional, cast

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from login.models import Login

from .models import User


class UserService:
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> User:
        return User.objects.create_user(**user_data)

    @staticmethod
    def create_login_record(
        user: User,
        request_meta: Dict[str, Any],
        is_success: bool = True,
    ) -> Optional[Login]:
        try:
            return Login.objects.create(
                user_num_id=user.id,
                user_ip=request_meta.get("REMOTE_ADDR", ""),
                user_agent=request_meta.get("HTTP_USER_AGENT", ""),
                is_success=is_success,
            )
        except Exception as e:
            print(f"Error creating login record: {str(e)}")
            return None

    @staticmethod
    def handle_login(user: User, request_meta: Dict[str, Any]) -> Dict[str, str]:
        try:
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(cast(RefreshToken, refresh).access_token),
            }

            UserService.create_login_record(user, request_meta)
            return tokens
        except Exception as e:
            print(f"Error handling login: {str(e)}")
            raise

    @staticmethod
    def handle_logout(user: User, refresh_token: str) -> bool:
        try:
            try:
                login = (
                    Login.objects.filter(user_num_id=user.id)
                    .order_by("-login_at")
                    .first()
                )
                if login:
                    login.logout_at = timezone.now()
                    login.save()
            except Exception as e:
                print(f"Error updating login record: {e}")

            return True
        except Exception as e:
            print(f"Logout error: {e}")
            return False

    @staticmethod
    def is_token_blacklisted(refresh_token: str) -> bool:
        # Redis 제거로 인해 항상 False 반환
        return False

    @staticmethod
    def deactivate_user(user: User) -> None:
        user.is_active = False
        user.save()
