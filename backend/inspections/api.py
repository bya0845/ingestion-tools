import io
import json
import zipfile
import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from documents.templates.weekly_schedule import create_schedules_as_bytes
from documents.templates.daily_logs import create_daily_logs_as_bytes
from src.input_parser import parse_entries_from_table, parse_tsv

logger = logging.getLogger(__name__)


@api_view(["POST"])
def preview_schedule(request):
    """Parses TSV data and returns preview entries for the frontend table."""
    logger.info("Preview schedule requested")
    raw_tsv = request.data.get("raw_tsv", "")
    if not raw_tsv.strip():
        logger.debug("Empty TSV data provided")
        return Response({"entries": [], "count": 0})
    logger.debug(f"Parsing TSV, length: {len(raw_tsv)}")
    try:
        entries = parse_tsv(raw_tsv)
    except ValueError as error:
        logger.error(f"TSV parse error: {error}")
        return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    serialized = [
        {
            "bin": e["bin"],
            "county": e["county"],
            "feature_carried": e["feature_carried"],
            "feature_crossed": e["feature_crossed"],
            "due_date": e["due_date"].strftime("%m/%d/%Y") if e.get("due_date") else "",
            "scheduled_date": e["scheduled_date"].strftime("%m/%d/%Y"),
            "access": e["access"],
            "lane_closed": e["lane_closed"],
            "town": e["town"],
        }
        for e in entries
    ]
    logger.debug(f"Serialized {len(serialized)} entries: {serialized}")
    return Response({"entries": serialized, "count": len(serialized)})


@api_view(["POST"])
def generate_schedule(request):
    """Generates schedule Excel files for browser download."""
    team_name = request.data.get("team_name", "")
    entries_json = request.data.get("entries_json", "")

    if not team_name:
        return Response(
            {"error": "Team name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not entries_json:
        return Response(
            {"error": "No entries provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        raw_entries = json.loads(entries_json)
    except json.JSONDecodeError:
        return Response(
            {"error": "Invalid entries JSON"}, status=status.HTTP_400_BAD_REQUEST
        )

    entries = parse_entries_from_table(raw_entries)
    if not entries:
        return Response(
            {"error": "No valid entries found"}, status=status.HTTP_400_BAD_REQUEST
        )

    results = create_schedules_as_bytes(entries, team_name)

    if not results:
        return Response(
            {"error": "Failed to generate schedules"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if len(results) == 1:
        filename, content = results[0]
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in results:
            zf.writestr(filename, content)
    buf.seek(0)
    response = HttpResponse(buf.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="schedules.zip"'
    response["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response


@api_view(["POST"])
def generate_daily_logs(request):
    """Generates daily log Excel files for browser download."""
    team_name = request.data.get("team_name", "")
    entries_json = request.data.get("entries_json", "")

    if not team_name:
        return Response(
            {"error": "Team name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not entries_json:
        return Response(
            {"error": "No entries provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        raw_entries = json.loads(entries_json)
    except json.JSONDecodeError:
        return Response(
            {"error": "Invalid entries JSON"}, status=status.HTTP_400_BAD_REQUEST
        )

    entries = parse_entries_from_table(raw_entries)
    if not entries:
        return Response(
            {"error": "No valid entries found"}, status=status.HTTP_400_BAD_REQUEST
        )

    results = create_daily_logs_as_bytes(entries, team_name)

    if not results:
        return Response(
            {"error": "Failed to generate daily logs"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if len(results) == 1:
        filename, content = results[0]
        response = HttpResponse(
            content,
            content_type="application/vnd.ms-excel.sheet.macroEnabled.12",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in results:
            zf.writestr(filename, content)
    buf.seek(0)
    response = HttpResponse(buf.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="daily_logs.zip"'
    response["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response
