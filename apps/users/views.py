import random
from datetime import datetime, timedelta
from typing import Any, cast

from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.logins.models import Login

from .models import User
from .serializers import UserCreateSerializer, VerificationSerializer


class UserSignupView(generics.CreateAPIView[User]):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class LoginView(TokenObtainPairView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            tokens = response.data
            user = User.objects.get(user_id=request.data["user_id"])
            cache.set(
                f"token:{user.user_id}", tokens["refresh"], timeout=60 * 60 * 24 * 7
            )
            Login.objects.create(
                user_num=user,
                user_ip=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                is_success=True,
            )
        return response


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
    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        code = str(random.randint(100000, 99999))
        user.verification_code = code
        user.code_created_at = timezone.now()
        user.save()

        # 이메일 발송
        send_mail(
            "인증 코드",
            f"인증 코드 : {code}",
            "from@example.com",
            [user.email],
            fail_silently=False,
        )
        return Response(status=status.HTTP_200_OK)


class VerifyCodeView(generics.GenericAPIView[User]):
    serializer_class = VerificationSerializer

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        code = request.data.get("verification_code")

        if (
            not user.code_created_at
            or timezone.now() > user.code_created_at + timedelta(minutes=5)
        ):
            return Response(
                {"error": "인증 코드가 만료되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if code == user.verification_code:
            user.email_verified = True
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response(
            {"error": "잘못된 인증 코드"}, status=status.HTTP_400_BAD_REQUEST
        )
