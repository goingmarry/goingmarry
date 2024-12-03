import uuid  # UUID 모듈을 사용하여 고유한 문자열 생성

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Planner

User = get_user_model()


class PlannerTests(APITestCase):
    """
    Planner API에 대한 테스트 케이스
    """

    def setUp(self) -> None:
        """
        각 테스트 메서드 실행 전에 호출되는 메서드.
        테스트 사용자 및 초기 데이터를 설정합니다.
        """
        # 고유한 이메일 주소 생성 (테스트 사용자 생성에 필요)
        unique_email = f"testuser_{uuid.uuid4()}@example.com"

        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            username="testuser", email=unique_email, password="testpass123"
        )

        # 사용자 로그인 처리 및 토큰 저장
        # 올바른 로그인 엔드포인트 사용
        response = self.client.post(
            reverse("user:login"),  # 올바른 엔드포인트로 수정
            {"username": "testuser", "password": "testpass123"},  # 로그인 데이터 수정
            format="json",
        )

        # 응답 데이터 확인 및 토큰 저장
        print("Login Response Status Code:", response.status_code)
        print("Login Response Data:", response.data)

        self.token = response.data["access"]

        # 인증 헤더 설정
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        # 테스트 플래너 생성
        self.planner = Planner.objects.create(
            user=self.user, ordering_num=1, title="Test Planner", is_delete=False
        )

        # API 엔드포인트 URL 설정
        self.planner_list_url = reverse("planner-list-create")
        self.planner_detail_url = reverse(
            "planner-detail", kwargs={"pk": self.planner.id}
        )

    def test_delete_planner(self) -> None:
        """
        특정 플래너를 삭제하는 API 테스트
        """

        response = self.client.delete(
            self.planner_detail_url
        )  # DELETE 요청으로 플래너 삭제

        # 응답 상태 코드가 204 No Content인지 확인
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 삭제된 플래너가 데이터베이스에 존재하지 않는지 확인
        self.assertFalse(Planner.objects.filter(id=self.planner.id).exists())
