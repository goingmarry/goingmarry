from typing import Any, cast

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User

from .models import Calendar

# Create your tests here.


class CalendarTests(APITestCase):
    def setUp(self) -> None:
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            nickname="testnick",
            email="test@test.com",
        )

        # JWT 토큰 설정
        refresh = RefreshToken.for_user(self.user)
        access_token = cast(Any, refresh).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(access_token)}")

    def test_create_calendar(self) -> None:
        # 캘린더 생성 테스트
        url = reverse("calendar:calendar-create")
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Calendar.objects.count(), 1)
        self.assertEqual(Calendar.objects.get().planner_id, self.user.id)

    def test_get_calendars(self) -> None:
        # 캘린더 조회 테스트
        # 테스트용 캘린더 생성
        Calendar.objects.create(planner_id=self.user.id)
        Calendar.objects.create(planner_id=self.user.id)

        url = reverse("calendar:calendar-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_calendar(self) -> None:
        # 캘린더 수정 테스트
        calendar = Calendar.objects.create(planner_id=self.user.id)

        url = reverse("calendar:calendar-update", args=[calendar.id])
        response = self.client.put(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def teest_delete_calendar(self) -> None:
        # 캘린더 삭제 테스트 (soft delete)
        calendar = Calendar.objects.create(planner_id=self.user.id)

        url = reverse("calendar:calendar-delete", args=[calendar.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Calendar.objects.get(id=calendar.id).is_deleted)

    def test_unauthorized_access(self) -> None:
        # 권한 없는 접근 테스트
        # 다른 사용자의 캘린더 생성
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpass123",
            nickname="othernick",
            email="other@other.com",
        )
        calendar = Calendar.objects.create(planner_id=other_user.id)

        # 수정 시도
        url = reverse("calendar:calendar-update", args=[calendar.id])
        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 삭제 시도
        url = reverse("calendar:calendar-delete", args=[calendar.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexistent_calendar(self) -> None:
        # 존재하지 않는 캘린더 접근 테스트
        url = reverse("calendar:calendar-update", args=[999])
        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
