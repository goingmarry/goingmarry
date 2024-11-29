from typing import Any, Dict

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserTests(APITestCase):
    def setUp(self) -> None:
        self.test_data = {
            "username": "testuser",
            "password": "testpass123",
            "nickname": "testnick",
            "email": "test@test.com",
        }
        cache.clear()

    def test_signup(self) -> None:
        url = reverse("user:signup")  # users -> user
        response = self.client.post(url, self.test_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")

    def test_login(self) -> None:
        self.test_signup()
        url = reverse("user:login")  # users -> user
        login_data = {
            "username": "testuser",
            "password": "testpass123",
        }
        response = self.client.post(url, login_data, format="json")
        print("Login Request Data:", login_data)  # 요청 데이터 출력
        print("Login Response:", response.data)  # 응답 데이터 출력
        print("Response Status:", response.status_code)  # 상태 코드 출력
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self) -> None:
        # 먼저 회원가입
        self.test_signup()
        # 로그인
        login_response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # 토큰 갱신
        url = reverse("user:token-refresh")
        response = self.client.post(url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)

    def test_logout(self) -> None:
        # 먼저 회원가입
        self.test_signup()
        # 로그인
        login_response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        tokens = login_response.data

        # 로그아웃
        url = reverse("user:logout")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.post(url, {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deactivate_user(self) -> None:
        # 먼저 회원가입
        self.test_signup()
        # 로그인
        login_response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        tokens = login_response.data

        # 계정 비활성화
        url = reverse("user:deactivate")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 비활성화된 계정으로 로그인 시도 테스트
        login_response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testDown(self) -> None:
        # 테스트 종료 후 실행되는 메서드
        User.objects.all().delete()
        cache.clear()
