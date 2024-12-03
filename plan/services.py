from typing import Any, Dict, List, Optional

from django.db.models.query import QuerySet

from user.models import User

from .models import Plan


class PlanService:
    @staticmethod
    def get_plans(user: "User", search_keyword: Optional[str] = None) -> QuerySet[Plan]:
        query = Plan.objects.filter(planner_id=user.id, is_deleted=False)  # 수정된 부분
        if search_keyword:
            query = query.filter(title__icontains=search_keyword)
        return query.order_by("ordering_num")

    @staticmethod
    def create_plan(data: Dict[str, Any], user: "User") -> Plan:
        # id을 planner로 설정
        data["planner_id"] = user.id  # user가 아닌 id으로 설정
        return Plan.objects.create(**data)

    @staticmethod
    def update_plan(plan_id: int, data: Dict[str, Any], user: "User") -> Plan:
        try:
            plan = Plan.objects.get(id=plan_id, planner_id=user.id)  # 수정된 부분
            print(f"Debug - Plan planner_id: {plan.planner_id}")
            print(f"Debug - User id: {user.id}")

            if plan.planner_id != user.id:
                print(f"Debug - Authorization failed: {plan.planner_id} != {user.id}")
                raise PermissionError("Not authorized to update this plan")

            # 데이터 업데이트
            for key, value in data.items():
                if hasattr(plan, key):  # 해당 필드가 있는지 확인
                    setattr(plan, key, value)

            plan.save()
            return plan

        except Plan.DoesNotExist:
            raise Plan.DoesNotExist(f"Plan with id {plan_id} does not exist")

    @staticmethod
    def delete_plan(plan_id: int, user: "User") -> bool:
        plan = Plan.objects.get(id=plan_id, planner_id=user.id)  # user.id 사용
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
