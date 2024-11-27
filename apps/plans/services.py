from typing import Any, Dict, List, Optional

from django.db.models.query import QuerySet

from apps.users.models import User

from .models import Plan


class PlanService:
    @staticmethod
    def get_plans(user: "User", search_keyword: Optional[str] = None) -> QuerySet[Plan]:
        query = Plan.objects.filter(
            planner_id=user.user_num, is_deleted=False
        )  # user.user_num 사용
        if search_keyword:
            query = query.filter(title__icontains=search_keyword)
        return query.order_by("ordering_num")

    @staticmethod
    def create_plan(data: Dict[str, Any], user: "User") -> Plan:
        return Plan.objects.create(**data)

    @staticmethod
    def update_plan(plan_id: int, data: Dict[str, Any], user: "User") -> Plan:
        plan = Plan.objects.get(
            id=plan_id, planner_id=user.user_num
        )  # user.user_num 사용
        for key, value in data.items():
            setattr(plan, key, value)
        plan.save()
        return plan

    @staticmethod
    def delete_plan(plan_id: int, user: "User") -> bool:
        plan = Plan.objects.get(
            id=plan_id, planner_id=user.user_num
        )  # user.user_num 사용
        plan.is_deleted = True
        plan.save()
        return True

    @staticmethod
    def update_plan_order(plans: List[Dict[str, Any]]) -> bool:
        for plan_data in plans:
            Plan.objects.filter(id=plan_data["id"]).update(
                ordering_num=plan_data["ordering_num"]
            )
        return True
