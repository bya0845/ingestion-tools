from django.urls import include, path

from inspections.api import generate_schedule, preview_schedule
from teams.api import list_teams

urlpatterns = [
    path("teams/", list_teams),
    path("inspections/preview/", preview_schedule),
    path("inspections/schedule/", generate_schedule),
]
