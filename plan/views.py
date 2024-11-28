from typing import Any, Dict, List, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from plan.models import Plan
from user.models import User

from .serializers import PlanSerializer
from .services import PlanService


class PlanListView(APIView):
    permission_classes = [IsAuthenticated]  # 추가

    def get(self, request: Request) -> Response:
        search_keyword = request.query_params.get("search")
        plans = PlanService.get_plans(cast(User, request.user), search_keyword)
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        """plan 순서 업데이트"""
        order_data = cast(List[Dict[str, Any]], request.data)  # 타입 캐스팅
        success = PlanService.update_plan_order(order_data)
        if success:
            return Response({"message": "Successfully updated order"})
        return Response(
            {"error": "Failed to update order"}, status=status.HTTP_400_BAD_REQUEST
        )


class PlanCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        plan = PlanService.create_plan(request.data, cast(User, request.user))
        serializer = PlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PlanUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # 추가

    def put(self, request: Request, plan_id: int) -> Response:
        try:
            # plan 업데이트 시도
            updated_plan = PlanService.update_plan(
                plan_id, request.data, cast(User, request.user)
            )
            # 성공시 serialize해서 반환
            serializer = PlanSerializer(updated_plan)
            return Response(serializer.data)

        except Plan.DoesNotExist:
            return Response(
                {"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PlanDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, plan_id: int) -> Response:
        """plan 삭제 (soft delete)"""
        PlanService.delete_plan(plan_id, cast(User, request.user))
        return Response({"message": "Successfully deleted"})
