from django.urls import path

from inspections import views

urlpatterns = [
    path("schedule/", views.generate_schedule, name="generate_schedule"),
]
