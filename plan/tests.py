from typing import Any, cast

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User

from .models import Plan


class PlanTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            user_id="testuser",
            password="testpass123",
            nickname="testnick",
            email="test@test.com",
        )

        self.plan_data = {
            "planner_id": self.user.user_num,  # planner -> planner_id
            "ordering_num": 1,
            "title": "Test Plan",
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
        }

        refresh = RefreshToken.for_user(self.user)
        access_token = cast(Any, refresh).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(access_token)}")

    def test_create_plan(self) -> None:
        """Plan 생성 테스트"""
        url = reverse("plans:plan-create")
        response = self.client.post(url, self.plan_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plan.objects.count(), 1)
        self.assertEqual(Plan.objects.get().title, "Test Plan")

    def test_get_plans(self) -> None:  # *args, **kwargs 제거
        Plan.objects.create(**self.plan_data)
        url = reverse("plans:plan-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_plans(self) -> None:  # *args, **kwargs 제거
        Plan.objects.create(**self.plan_data)
        url = reverse("plans:plan-list")
        response = self.client.get(f"{url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Test Plan", str(response.data))

        response = self.client.get(f"{url}?search=NoResult")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("Test Plan", str(response.data))

    def test_update_plan(self) -> None:  # *args, **kwargs 제거
        plan = Plan.objects.create(**self.plan_data)
        url = reverse("plans:plan-update", args=[plan.id])
        updated_data = {
            "title": "Updated Test Plan",
            "start_date": "2024-01-03",
            "end_date": "2024-01-04",
        }
        response = self.client.put(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Plan.objects.get(id=plan.id).title, "Updated Test Plan")

    def test_delete_plan(self) -> None:  # 삭제 테스트 추가
        plan = Plan.objects.create(**self.plan_data)
        url = reverse("plans:plan-delete", args=[plan.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Plan.objects.get(id=plan.id).is_deleted)
