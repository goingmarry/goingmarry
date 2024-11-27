from typing import Any, Dict

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserTests(APITestCase):
    def setUp(self) -> None:
        # 테스트 시작 전 실행되는 메서드
        # 테스트 유저 데이터
        self.user_data: Dict[str, str] = {
            "user_id": "testuser",
            "password": "testpass123",
            "nickname": "testnick",
            "email": "test@test.com",
        }
        # 테스트 전 캐시 초기화
        cache.clear()

    def test_signup(self) -> None:
        # 회원 가입 테스트
        url = reverse("users:signup")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().user_id, "testuser")

    def test_login(self) -> None:
        # 로그인 테스트
        # 회원 가입
        self.test_signup()

        url = reverse("users:login")
        login_data = {
            "user_id": "testuser",
            "password": "testpass123",
        }
        response = self.client.post(url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self) -> None:
        # 토큰 갱신 테스트
        # 로그인
        self.test_login()
        url = reverse("users:token-refresh")
        refresh_token = self.client.post(
            reverse("users:login"),
            {"user_id": "testuser", "password": "testpass123"},
            format="json",
        ).data["refresh"]

        response = self.client.post(url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout(self) -> None:
        # 로그아웃 테스트
        # 로그인
        self.test_login()
        url = reverse("users:logout")

        # 로그인 해서 토큰 받기
        tokens = self.client.post(
            reverse("users:login"),
            {"user_id": "testuser", "password": "testpass123"},
            format="json",
        ).data

        # Authorization 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.post(url, {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deactivate_user(self) -> None:
        # 회원 비활성화 테스트
        # 로그인
        self.test_login()
        url = reverse("users:deactivate")

        # 로그인 응답으로부터 토큰 받기
        login_response = self.client.post(
            reverse("users:login"),
            {"user_id": "testuser", "password": "testpass123"},
            format="json",
        )

        # Response 에서 .data로 접근
        tokens = login_response.data

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

        # Authorization 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 비활성화된 계정으로 로그인 시도
        login_response = self.client.post(
            reverse("users:login"),
            {"user_id": "testuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def testDown(self) -> None:
        # 테스트 종료 후 실행되는 메서드
        User.objects.all().delete()
        cache.clear()
