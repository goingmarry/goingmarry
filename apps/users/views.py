from typing import Any, cast

from django.core.cache import cache
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.logins.models import Login

from .models import User
from .serializers import UserCreateSerializer


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
