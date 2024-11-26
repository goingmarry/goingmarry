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
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.logins.models import Login
from trip import settings

from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserCreateSerializer,
    VerificationSerializer,
)


class UserSignupView(generics.CreateAPIView[User]):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer  # type: ignore

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            user = User.objects.get(user_id=request.data.get("user_id"))
            if not user.is_active:
                return Response(
                    {"error": "Account is not active"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
                )

            response = Response(serializer.validated_data, status=status.HTTP_200_OK)

            # 토큰 저장 및 로그인 기록
            tokens = serializer.validated_data
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

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(generics.GenericAPIView[User]):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        refresh_token = cache.get(f"token:{user.user_id}")
        if refresh_token:
            cache.delete(f"token:{user.user_id}")
            login = Login.objects.filter(user_num=user).latest("login_at")
            login.logout_at = timezone.now()
            login.save()
        return Response(status=status.HTTP_200_OK)


class UserDeactivateView(generics.UpdateAPIView[User]):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = cast(User, request.user)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_200_OK)


class SendVerificationView(generics.GenericAPIView[User]):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)

        # 이미 인증된 사용자 체크
        if user.email_verified:
            return Response(
                {"error": "Email already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = "".join(str(random.randint(0, 9)) for _ in range(6))
        user.verification_code = code
        user.code_created_at = timezone.now()
        user.save()

        try:
            # 이메일 발송
            send_mail(
                "[Trip] 이메일 인증 코드",
                f"인증 코드 : {code}\n이 코드는 5분간 유효합니다.",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response(
                {"message": "Verification code sent"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyCodeView(generics.GenericAPIView[User]):
    permission_classes = [IsAuthenticated]
    serializer_class = VerificationSerializer

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        code = request.data.get("verification_code")

        # 코드 만료 체크 (5분))
        if (
            not user.code_created_at
            or timezone.now() > user.code_created_at + timedelta(minutes=5)
        ):
            return Response(
                {"error": "Verification code has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code:
            return Response(
                {"error": "Verification code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if code != user.verification_code:
            return Response(
                {"error": "Invalid verification code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True
        user.verification_code = None  # 사용된 코드 제거
        user.code_created_at = None
        user.save()

        return Response(
            {"message": "Email successfully verified"},
            status=status.HTTP_200_OK,
        )
