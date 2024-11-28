# 타입 힌트를 위해 Python의 typing 모듈에서 필요한 도구들을 가져옴
# Any: 어떤 타입이든 허용, Dict : 딕셔너리 타입, Optional : None을 포함할 수 있는 타입, cast : 타입 변환 함수
from typing import Any, Dict, Optional, cast

# 비밀번호를 해시화(암호화) 하기 위해 Django의 인증 모듈에서 make_password 함수 가져오기)
from django.contrib.auth.hashers import make_password

# Django의 캐시 시스템을 사용하기 위해 cache 모듈 가져오기
from django.core.cache import cache

# 현재 시간과 관련된 작업을 위해 Django의 timezone 유틸리티 가져오기
from django.utils import timezone

# SimpleJwt에서 제공하는 RefreshToken 클래스를 가져와 토큰 생성에 사용
from rest_framework_simplejwt.tokens import RefreshToken

# 로그인 기록을 저장하는 Login 모델 가져오기
from login.models import Login

# 같은 앱에 정의된 사용자 모델(User) 가져오기
from .models import User


# 사용자 관련 기능을 모아놓은 서비스 클래스 정의
class UserService:
    @staticmethod
    # 새로운 사용자를 생성하는 메서드
    def create_user(user_data: Dict[str, Any]) -> User:
        # create_user 메서드를 호출하여 사용자 데이터를 기반으로 User 객체 생성
        return User.objects.create_user(**user_data)

    @staticmethod
    def create_login_record(
        # 로그인 기록을 생성하는 메서드
        user: User,
        request_meta: Dict[str, Any],
        is_success: bool = True,
    ) -> Optional[Login]:
        try:
            return Login.objects.create(
                # 로그인을 시도한 사용자 객체 연결
                user_num=user,
                # 클라이언트의 IP 주소
                user_ip=request_meta.get("REMOTE_ADDR", ""),
                # 브라우저/기기 정보
                user_agent=request_meta.get("HTTP_USER_AGENT", ""),
                # 로그인 성공 여부 (기본값 :True)
                is_success=is_success,
            )
        except Exception as e:
            # 예외 발생 시 에러 메시지를 출력하고 None 반환
            print(f"Error creating login record: {str(e)}")
            return None

    @staticmethod
    # 사용자의 로그인 정보를 처리하고, 액세스 및 리프레시 토큰 반환
    def handle_login(user: User, request_meta: Dict[str, Any]) -> Dict[str, str]:
        try:
            # 사용자 객체를 기반으로 리프레시 토큰 생성
            refresh = RefreshToken.for_user(user)

            tokens = {
                # 리프레시 토큰 문자열로 변환
                "refresh": str(refresh),
                "access": str(
                    # 리프레시 토큰에서 액세스 토큰 추출 후 문자열로 변환
                    cast(RefreshToken, refresh).access_token
                ),
            }

            # 캐시에 토큰 저장 (사용자의 user_id를 키로 사용)
            cache.set(
                # 저장 시간 : 7일(초 단위로 설정)
                f"token:{user.user_id}",
                tokens["refresh"],
                timeout=60 * 60 * 24 * 7,
            )

            # 로그인 기록 생성
            UserService.create_login_record(user, request_meta)

            # 생성된 토큰 반환
            return tokens
        except Exception as e:
            # 에러 발생 시 메시지 출력 후 예외 재발생
            print(f"Error handling login: {str(e)}")
            raise

    @staticmethod
    # 로그아웃 요청을 처리하는 메서드
    def handle_logout(user: User, refresh_token: str) -> bool:
        try:
            # 블랙리스트에 리프레시 토큰 추가
            blacklist_key = f"blacklist:{refresh_token}"
            # 블랙리스트 토큰 7일 동안 유지
            cache.set(blacklist_key, "true", timeout=60 * 60 * 24 * 7)

            # 로그아웃 시간 기록
            try:
                login = (
                    # 해당 사용자의 가장 최근 로그인 기록 가져오기
                    Login.objects.filter(user_num=user)
                    .order_by("-login_at")
                    .first()
                )
                if login:
                    # 현재 시간을 로그아웃 시간으로 설정
                    login.logout_at = timezone.now()
                    # 로그인 기록 저장
                    login.save()
            except Exception as e:
                # 로그아웃 시간 기록 중 예외 발생 시 메시지 출력
                print(f"Error updating login record: {e}")

            # 로그아웃 성공 시 True 반환
            return True

        except Exception as e:
            # 로그아웃 처리 중 에러 발생 시 메시지 출력 후 False 반환
            print(f"Logout error: {e}")
            return False

    @staticmethod
    def is_token_blacklisted(refresh_token: str) -> bool:
        """
        주어진 refresh 토큰이 블랙리스트에 포함되어 있는지 확인

        Args:
            refresh_token (str): 확인할 refresh 토큰

        Returns:
            bool: 블랙리스트에 포함되어 있으면 True, 아니면 False
        """

        # 캐시에서 해당 리프레시 토큰의 블랙리스트 여부 확인
        return bool(cache.get(f"blacklist:{refresh_token}"))

    @staticmethod
    def deactivate_user(user: User) -> None:
        """
        사용자를 비활성화

        Args:
            user (User): 비활성화할 사용자 객체
        """

        # 사용자의 활성 상태를 비활성화로 변경
        user.is_active = False
        # 변경된 사용자 정보 저장
        user.save()
