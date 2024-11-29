import hashlib  # 상단에 import 추가
from typing import Any, Dict, Optional, cast

from django.contrib.auth.hashers import make_password
from django.core.cache import cache
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

            # 토큰을 해시로 변환하여 저장
            hashed_token = hashlib.md5(tokens["refresh"].encode()).hexdigest()
            cache.set(
                f"token:{hashed_token}",
                "true",
                timeout=60 * 60 * 24 * 7,
            )

            UserService.create_login_record(user, request_meta)
            return tokens
        except Exception as e:
            print(f"Error handling login: {str(e)}")
            raise

    @staticmethod
    def handle_logout(user: User, refresh_token: str) -> bool:
        try:
            # 토큰을 해시로 변환하여 짧은 키 생성
            hashed_token = hashlib.md5(refresh_token.encode()).hexdigest()
            blacklist_key = f"bl:{hashed_token}"
            cache.set(blacklist_key, "true", timeout=60 * 60 * 24 * 7)

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
        # 토큰을 해시로 변환하여 검색
        hashed_token = hashlib.md5(refresh_token.encode()).hexdigest()
        return bool(cache.get(f"bl:{hashed_token}"))

    @staticmethod
    def deactivate_user(user: User) -> None:
        user.is_active = False
        user.save()
