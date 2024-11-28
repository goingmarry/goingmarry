from django.urls import path

from . import views

app_name = "plans"

urlpatterns = [
    path("", views.PlanListView.as_view(), name="plan-list"),
    path("create/", views.PlanCreateView.as_view(), name="plan-create"),
    path("<int:plan_id>/", views.PlanUpdateView.as_view(), name="plan-update"),
    path("<int:plan_id>/delete/", views.PlanDeleteView.as_view(), name="plan-delete"),
]
