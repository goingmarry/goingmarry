from typing import Optional, cast

from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response

from plan.models import Plan
from plan.services import PlanService  # 이미 임포트 되어 있는 PlanService 사용
from user.models import User as CustomUser  # 커스텀 User 모델


# PlanSerializer에서 ModelSerializer에 대한 타입을 명시적으로 지정합니다.
class PlanSerializer(serializers.ModelSerializer[Plan]):
    class Meta:
        model = Plan
        fields = "__all__"

    def get(self, request: Request) -> Response:
        search_keyword: Optional[str] = request.query_params.get("search_keyword", None)
        plans = PlanService.get_plans(cast(CustomUser, request.user), search_keyword)
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)
