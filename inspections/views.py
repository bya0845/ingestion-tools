import io
import json
import zipfile
from pathlib import Path

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from documents.creators import create_schedules_as_bytes
from src.input_parser import parse_entries_from_table, parse_tsv
from teams.models import Team


@require_http_methods(["GET", "POST"])
def generate_schedule(request):
    """Renders the schedule generation form and returns a preview of parsed inspection entries.

    On action=generate, creates one weekly schedule file per week for the selected team.
    The output directory is persisted in the session and defaults to the project output/ folder.
    """
    team_choices = [
        (t.team_leader.split()[-1], t.team_leader)
        for t in Team.objects.order_by("team_leader")
    ]
    entries = []
    raw_tsv = ""
    selected_team = ""
    output_dir_str = request.session.get("output_dir", "")

    if request.method == "POST":
        raw_tsv = request.POST.get("raw_tsv", "")
        selected_team = request.POST.get("team_name", "")
        action = request.POST.get("action", "")

        entries_json_raw = request.POST.get("entries_json", "").strip()
        if entries_json_raw and action == "generate":
            try:
                entries = parse_entries_from_table(json.loads(entries_json_raw))
            except (json.JSONDecodeError, ValueError):
                entries = parse_tsv(raw_tsv)
        else:
            entries = parse_tsv(raw_tsv)

        new_output_dir = request.POST.get("output_dir", "").strip()
        if new_output_dir:
            request.session["output_dir"] = new_output_dir
            output_dir_str = new_output_dir
        elif "output_dir" in request.session:
            del request.session["output_dir"]
            output_dir_str = ""

        if action == "generate" and entries and selected_team:
            output_dir = Path(output_dir_str) if output_dir_str else None
            results = create_schedules_as_bytes(entries, selected_team, output_dir=output_dir)
            if results:
                if len(results) == 1:
                    filename, content = results[0]
                    response = HttpResponse(
                        content,
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    response["Content-Disposition"] = f'attachment; filename="{filename}"'
                    return response
                else:
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        for filename, content in results:
                            zf.writestr(filename, content)
                    buf.seek(0)
                    response = HttpResponse(buf.read(), content_type="application/zip")
                    response["Content-Disposition"] = 'attachment; filename="schedules.zip"'
                    return response

    return render(request, "inspections/schedule.html", {
        "team_choices": team_choices,
        "selected_team": selected_team,
        "entries": entries,
        "raw_tsv": raw_tsv,
        "entry_count": len(entries),
        "output_dir": output_dir_str,
    })
