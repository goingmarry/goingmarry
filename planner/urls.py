from django.urls import path

from .views import PlannerDetailView, PlannerListCreateView

urlpatterns = [
    # 플래너 목록 조회 및 생성
    path("create/", PlannerListCreateView.as_view(), name="planner-list-create"),
    # 특정 플래너 조회, 수정 및 삭제
    path("<int:pk>/", PlannerDetailView.as_view(), name="planner-detail"),
]
