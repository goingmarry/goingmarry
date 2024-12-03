from typing import Any  # Any 타입을 사용하기 위해 추가

from django.contrib.auth import get_user_model  # User 모델을 가져오기 위해 추가
from django.db.models import QuerySet  # QuerySet 타입을 사용하기 위해 추가
from rest_framework import generics, permissions
from rest_framework.serializers import (
    BaseSerializer,
)  # BaseSerializer를 사용하기 위해 추가

from .models import Planner
from .serializers import PlannerSerializer

User = get_user_model()  # 현재 프로젝트의 User 모델 가져오기


class PlannerListCreateView(
    generics.ListCreateAPIView[Planner]
):  # 제네릭 타입 매개변수 추가
    """
    여행 플래너 목록 조회 및 생성 API
    """

    queryset = Planner.objects.all()  # 모든 Planner 객체를 쿼리셋으로 가져옵니다.
    serializer_class = PlannerSerializer  # 사용할 직렬화 클래스 지정
    permission_classes = [permissions.IsAuthenticated]  # 인증된 사용자만 접근 가능

    def perform_create(
        self, serializer: BaseSerializer[Any]
    ) -> None:  # BaseSerializer에 Any 타입 매개변수 추가
        """
        새 플래너를 생성할 때 호출되는 메서드.
        현재 로그인한 사용자를 플래너의 사용자 필드에 자동으로 설정합니다.
        """
        if isinstance(self.request.user, User):  # 사용자 타입 확인
            serializer.save(user=self.request.user)  # 현재 사용자로 플래너를 저장


class PlannerDetailView(
    generics.RetrieveUpdateDestroyAPIView[Planner]
):  # 제네릭 타입 매개변수 추가
    """
    특정 여행 플래너 조회, 수정 및 삭제 API
    """

    queryset = Planner.objects.all()  # 모든 Planner 객체를 쿼리셋으로 가져옵니다.
    serializer_class = PlannerSerializer  # 사용할 직렬화 클래스 지정
    permission_classes = [permissions.IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get_queryset(self) -> QuerySet[Planner]:  # 반환 타입 주석 추가
        """
        현재 로그인한 사용자가 소유한 플래너만 반환합니다.
        """
        if self.request.user.is_authenticated:
            return self.queryset.filter(
                user=self.request.user
            )  # 인증된 사용자의 경우 필터링 수행
        return self.queryset.none()  # 비인증 사용자의 경우 빈 쿼리셋 반환
