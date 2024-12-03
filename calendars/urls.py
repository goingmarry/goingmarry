from django.urls import path

from . import views

app_name = "calendar"

urlpatterns = [
    path("", views.CalendarListView.as_view(), name="calendar-list"),
    path("create/", views.CalendarCreateView.as_view(), name="calendar-create"),
    path(
        "<int:calendar_id>/", views.CalendarUpdateView.as_view(), name="calendar-update"
    ),
    path(
        "<int:calendar_id>/delete/",
        views.CalendarDeleteView.as_view(),
        name="calendar-delete",
    ),
]
