from rest_framework.decorators import api_view
from rest_framework.response import Response

from teams.models import Team


@api_view(["GET"])
def list_teams(request):
    """Returns list of teams for dropdown selection."""
    teams = Team.objects.order_by("team_leader")
    data = [
        {
            "value": t.team_leader.split()[-1],
            "label": t.team_leader,
        }
        for t in teams
    ]
    return Response(data)
