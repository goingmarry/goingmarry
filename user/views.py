# 타입 힌팅을 위해 필요한 모듈
from typing import Any, cast

# HTTP 상태 코드 관리하는 모듈
from rest_framework import status

# 인증된 사용자만 접근을 허용하는 권한 클래스
from rest_framework.permissions import IsAuthenticated

# DRF의 Request 클래스를 임포트하여 응답 객체를 생성
from rest_framework.request import Request

# DRF의 Response 클래스를 임포트하여 응답 객체를 사용
from rest_framework.response import Response

# APIView를 상속받아 HTTP 요청을 처리하는 뷰 클래스를 생성
from rest_framework.views import APIView

# JWT토큰 관련 처리를 위한 RefreshToken 임포트
from rest_framework_simplejwt.tokens import RefreshToken

from django.shortcuts import render, redirect  # redirect 추가
from django.contrib.auth import login  # login 함수 임포트 추가
from .models import User
from .serializers import UserCreateSerializer
from .services import UserService


# 사용자 회원가입을 처리하는 뷰 클래스
class SignupView(APIView):
    def get(self, request):
        # 회원가입 폼을 렌더링
        return render(request, 'signup.html')

    # 요청으로 받은 데이터로 UserCreateSerializer 객체 생성
    def post(self, request: Request) -> Response:
        serializer = UserCreateSerializer(data=request.data)

        # 직렬화된 데이터가 유효한지 확인
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')

            # 사용자 이름과 이메일이 이미 존재하는지 확인
            if User.objects.filter(username=username).exists():
                # 사용자 이름이 이미 존재할 경우 오류 메시지를 템플릿에 전달
                return render(request, 'signup.html', {'error': '존재하는 계정입니다.'})

            if User.objects.filter(email=email).exists():
                # 이메일이 이미 등록된 경우 오류 메시지를 템플릿에 전달
                return render(request, 'signup.html', {'error': '이미 등록된 이메일입니다.'})

            try:
                # 유효한 데이터로 사용자 생성
                user = UserService.create_user(serializer.validated_data)
                # 사용자 생성 성공 시 응답 반환 (201 Created)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                # 예외 발생 시 오류 메시지 반환 (400 Bad Request)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 직렬화된 데이터가 유효하지 않으면 오류 메시지 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 사용자 로그인 처리를 위한 뷰 클래스
class LoginView(APIView):
    def get(self, request):
        # 로그인 폼을 렌더링
        return render(request, 'login.html')

    def post(self, request: Request) -> Response:
        # 요청 데이터에서 username과 password 추출
        username = request.data.get("username")
        password = request.data.get("password")

        # username과 password가 없으면 오류 메시지 반환
        if not username or not password:
            return Response(
                {"error": "Both username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 주어진 username 사용자 검색
            user = User.objects.get(username=username)
            # 비밀번호가 맞는지 확인
            if user.check_password(password):
                # 비활성 사용자일 경우 오류 메시지 반환
                if not user.is_active:
                    return Response(
                        {"error": "User account is not active"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                # 로그인 처리 후 plan 목록 페이지로 리다이렉트
                login(request, user)  # Django의 login 함수 사용
                return redirect('plan:plan-list')  # 계획 목록 페이지로 리다이렉트
            else:
                # 비밀번호가 잘못된 경우 오류 메시지 반환
                return Response(
                    {"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            # 사용자가 존재하지 않는 경우 오류 메시지 반환
            return Response(
                {"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # 예외가 발생한 경우 내부 서버 오류 메시지 반환
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 사용자 로그아웃 처리를 위한 뷰 클래스
class LogoutView(APIView):
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        try:
            # 현재 요청한 사용자를 user 객체로 변환
            user = cast(User, request.user)
            # 요청 데이터에서 refresh token 추출
            refresh_token = request.data.get("refresh")

            # refresh token이 없는 경우 오류 메시지 반환
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # 로그아웃 처리
            if UserService.handle_logout(user, refresh_token):
                return Response(
                    {"message": "Successfully logged out"}, status=status.HTTP_200_OK
                )

            # 로그아웃 처리 실패 시 오류 메시지 반환
            return Response(
                {"error": "Logout failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            # 예외 발생 시 오류 메시지 반환
            return Response(
                {"error": f"Logout error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 리프레시 토큰을 사용하여 액세스 토큰을 갱신하는 뷰 클래스
class TokenRefreshView(APIView):
    def post(self, request: Request) -> Response:
        # 요청 데이터에서 refresh token 추출
        refresh_token = request.data.get("refresh")

        # refresh token 이 없는 경우 오류 메시지 반환
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 블랙리스트에 있는지 확인
        if UserService.is_token_blacklisted(refresh_token):
            return Response(
                {"error": "Token is blacklisted"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            # RefreshToken 객체를 사용하여 액세스 토큰 갱신
            refresh = RefreshToken(refresh_token)
            return Response(
                {"access": str(refresh.access_token)}, status=status.HTTP_200_OK
            )
        except Exception:
            # 토큰이 잘못된 경우 오류 메시지 반환
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
            )


# 사용자의 계정을 비활성화하는 뷰 클래스
class UserDeactivateView(APIView):
    # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request) -> Response:
        try:
            # 요청한 사용자를 user 객체로 변환
            user = cast(User, request.user)
            # 사용자 계정을 비활성화
            UserService.deactivate_user(user)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            # 예외 발생 시 오류 메시지 반환
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
