import random
from datetime import datetime, timedelta
from typing import Any, Type, cast

from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.logins.models import Login
from trip import settings

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    NicknameUpdateSerializer,
    UserCreateSerializer,
    VerificationSerializer,
)


# 회원가입 뷰 - CreateAPIView를 사용해 User를 생성하는 API
class UserSignupView(generics.CreateAPIView[User]):
    # User 모델의 모든 데이터를 쿼리셋으로 사용
    queryset = User.objects.all()
    # User 생성에 사용할 시리얼라이저 지정
    serializer_class = UserCreateSerializer


# 로그인 뷰 - JWT 토큰 발급을 처리
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer  # type: ignore

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            tokens = response.data
            user = User.objects.get(user_id=request.data["user_id"])
            # Redis에 리프레시 토큰 저장
            cache.set(
                f"token:{user.user_id}", tokens["refresh"], timeout=60 * 60 * 24 * 7
            )
            Login.objects.create(
                user_num=user,
                user_ip=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                is_successful=True,
            )
        return response


# 로그아웃 뷰 - 캐시와 로그인 기록을 갱신
class LogoutView(generics.GenericAPIView[User]):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        try:
            user = cast(User, request.user)
            refresh_token = request.data.get("refresh")  # 변수명 변경

            if refresh_token:  # 변수명 변경
                # 리프레시 토큰 블랙리스트에 추가
                cache.set(
                    f"blacklist:{refresh_token}",  # 변수명 변경
                    "blacklisted",
                    timeout=60 * 60 * 24 * 7,  # 7일
                )
                # 기존 토큰 삭제
                cache.delete(f"token:{user.user_id}")

                try:
                    # 로그아웃 기록
                    login = Login.objects.filter(user_num=user).latest("login_at")
                    login.logout_at = timezone.now()
                    login.save()
                except Login.DoesNotExist:
                    pass

                return Response(
                    {"message": "Successfully logged out"}, status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"error": f"An error occurred during logout: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 사용자 비활성화 뷰 - 계정 상태 변경
class UserDeactivateView(generics.UpdateAPIView[User]):
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 현재 요청 사용자
        user = cast(User, request.user)
        # 계정 비활성화
        user.is_active = False
        # 상태 저장
        user.save()
        # 성공 응답
        return Response(status=status.HTTP_200_OK)


# 인증 코드 발송 뷰 - 이메일로 인증 코드 전송
class SendVerificationView(generics.GenericAPIView[User]):
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)

        # 이미 인증된 이메일인지 확인
        if user.email_verified:
            return Response(
                {"error": "Email already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 인증 코드 생성 (6자리 랜덤 숫자)
        code = "".join(str(random.randint(0, 9)) for _ in range(6))
        user.verification_code = code  # 생성한 코드 저장
        user.code_created_at = timezone.now()  # 코드 생성 시간 저장
        user.save()

        try:
            # 이메일 발송
            send_mail(
                "[Trip] 이메일 인증 코드",
                f"인증 코드 : {code}\n이 코드는 5분간 유효합니다.",
                settings.EMAIL_HOST_USER,
                [user.email],  # 사용자의 이메일 주소
                fail_silently=False,  # 에러 발생 시 예외 발생
            )
            return Response(
                {"message": "Verification code sent"}, status=status.HTTP_200_OK
            )
        # 이메일 발송 실패 시
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 인증 코드 확인 뷰 - 발송된 인증 코드를 검증
class VerifyCodeView(generics.GenericAPIView[User]):
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]
    # 인증 코드 검증용 시리얼라이저
    serializer_class = VerificationSerializer

    def post(self, request: Request) -> Response:
        # 현재 요청 사용자
        user = cast(User, request.user)
        # 요청 데이터에서 코드 추출
        code = request.data.get("verification_code")

        # 코드 만료 체크 (5분)
        if (
            not user.code_created_at
            or timezone.now() > user.code_created_at + timedelta(minutes=5)
        ):
            return Response(
                {"error": "Verification code has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 인증 코드가 제공되지 않은 경우
        if not code:
            return Response(
                {"error": "Verification code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 코드가 일치하지 않는 경우
        if code != user.verification_code:
            return Response(
                {"error": "Invalid verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이메일 인증 완료 처리
        # 인증 상태로 변경
        user.email_verified = True
        # 사용한 인증 코드는 삭제
        user.verification_code = None
        # 인증 코드 생성 시간 초기화
        user.code_created_at = None
        user.save()

        return Response(
            {"message": "Email successfully verified"},
            status=status.HTTP_200_OK,
        )


class NicknameUpdateView(generics.UpdateAPIView[User]):
    permisson_classes = [IsAuthenticated]
    serializer_class = NicknameUpdateSerializer

    def get_object(self) -> User:
        return cast(User, self.request.user)

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Nickname updated successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        refresh_token = request.data.get("refresh")

        # Redis에서 블랙리스트 확인
        if cache.get(f"blacklist:{refresh_token}"):
            return Response(
                {"error": "Token is blacklisted"}, status=status.HTTP_400_BAD_REQUEST
            )

        response = super().post(request, *args, **kwargs)
        return response
