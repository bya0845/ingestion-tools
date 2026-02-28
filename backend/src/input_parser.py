from datetime import datetime
import logging

from inspections.models import County
from src.utils import get_sunday

logger = logging.getLogger(__name__)

LANE_CLOSED_TRIGGERS = {"WZTC", "BT", "UB60", "UB50", "UB40"}

# Column offsets relative to the BIN column in the master spreadsheet TSV.

MASTER_SCHEDULE_COLUMNS: dict[str, int] = {
    "county": 0,
    "bin": 1,
    "feature_carried": 2,
    "feature_crossed": 3,
    "prev_inspection_due_date": 5,
    "due_date": 6,
    "gr": 9,
    "access": 15,
    "scheduled_date": 16,
    "town": 19,
}


def _parse_single_date(token: str, year: int | None = None) -> datetime | None:
    """Parses a single date token into a datetime.

    Tries formats: %m/%d/%y, %m/%d/%Y, then %m/%d (defaults to given year).
    Returns None if no format matches.
    """
    if year is None:
        year = datetime.now().year
    token = token.strip()
    if len(token) == 4:
        # Handle MMDD format without delimiters (e.g. 1107 = Nov 7)
        try:
            dt = datetime.strptime(token, "%m%d")
            return dt.replace(year=year)
        except ValueError:
            return None
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(token, fmt)
        except ValueError:
            pass
    try:
        dt = datetime.strptime(token, "%m/%d")
        return dt.replace(year=year)
    except ValueError:
        return None


def parse_scheduled_dates(raw: str, year: int = 2025) -> list[datetime]:
    """Parses a booked-access date string into a list of datetimes.

    Handles single dates ("10/14/25" or "10/14"), ampersand-separated dates,
    and inclusive ranges ("10/14/25 to 10/16/25"). Silently skips unparseable tokens.
    """
    raw = raw.strip()
    raw_lower = raw.lower()

    delimiter = None
    if " to " in raw_lower:
        delimiter = " to "
    elif "&" in raw:
        delimiter = "&"

    if not delimiter:
        dt = _parse_single_date(raw, year)
        if not dt:
            raise ValueError(f"Invalid date: could not parse '{raw}'")
        return [dt]

    dates = []
    for part in raw.split(delimiter):
        dt = _parse_single_date(part.strip(), year)
        if not dt:
            raise ValueError(f"Invalid date: could not parse '{part.strip()}'")
        dates.append(dt)

    if len(dates) != 2:
        raise ValueError(f"Date range must have exactly 2 dates, got {len(dates)}")
    return dates


def wztc(access: str | None) -> str:
    """Returns Y if access type requires lane closure, N otherwise."""
    if not access:
        return "N"
    return "Y" if any(t in access for t in LANE_CLOSED_TRIGGERS) else "N"


def get_county_name(county_id: int) -> str:
    """Returns county name from the database by ID."""
    try:
        return County.objects.get(id=county_id).name
    except County.DoesNotExist:
        logger.debug(f"County ID {county_id} not found in database")
        return ""


def parse_entries_from_table(raw_entries: list[dict]) -> list[dict]:
    """Converts table-cell entry dicts (from the preview) into inspection entry dicts.

    Assumes dates are in %m/%d/%Y format from parse_tsv serialization.
    Sorts entries by scheduled_date (earliest first).
    """
    entries = []
    for e in raw_entries:
        scheduled_date = datetime.strptime(e["scheduled_date"], "%m/%d/%Y")
        due_date = None
        due_raw = e.get("due_date", "")
        if due_raw and due_raw != "-":
            due_date = datetime.strptime(due_raw, "%m/%d/%Y")
        entries.append(
            {
                "team": "",
                "scheduled_date": scheduled_date,
                "due_date": due_date,
                "region": "8",
                "county": e.get("county", ""),
                "bin": e.get("bin", ""),
                "feature_carried": e.get("feature_carried", ""),
                "feature_crossed": e.get("feature_crossed", ""),
                "access": e.get("access", ""),
                "town": e.get("town", ""),
                "lane_closed": e.get("lane_closed", "N"),
            }
        )
    return sorted(entries, key=lambda x: x["scheduled_date"])


def parse_tsv(raw: str, year: int | None = None) -> list[dict]:
    """Parses tab-separated text pasted from Excel into a list of inspection entry dicts.

    Skips rows with no BIN, no scheduled date, or an unparseable scheduled date.
    Due date is expected in MMDD format (e.g. 1107 = Nov 7); year defaults to current year.
    """
    if year is None:
        year = datetime.now().year

    entries = []

    for line in raw.splitlines():
        cols = line.split("\t")

        single_row_values = {}
        for field_name, col_index in MASTER_SCHEDULE_COLUMNS.items():
            single_row_values[field_name] = (
                cols[col_index].strip() if col_index < len(cols) else ""
            )
        if not (single_row_values["bin"] and single_row_values["scheduled_date"]):
            logger.error(
                f"Each row must have a BIN and scheduled date. Skipping row with empty BIN or scheduled date: '{line}'"
            )
            continue

        # county validation and parsing
        cty = cols[MASTER_SCHEDULE_COLUMNS["county"]].strip()
        cty = single_row_values["county"]
        if not (cty.isdigit() and int(cty) < 10):
            raise ValueError(
                f"Invalid TSV format: expected county ID in first column, got '{cty}'"
            )
        county = get_county_name(int(cty))

        # scheduled date validation and parsing
        sched_raw = single_row_values["scheduled_date"].strip()
        try:
            scheduled_dates = parse_scheduled_dates(sched_raw)
        except ValueError:
            logger.error(f"Skipping row with unparseable scheduled date: '{sched_raw}'")
            continue

        # due date validation and parsing
        due_raw = single_row_values["due_date"]
        due_date = None
        if due_raw:
            due_date = _parse_single_date(due_raw, year)
            if due_date is None:
                logger.error(f"Invalid due date format: '{due_raw}'")

        base = {
            "team": "",
            "due_date": due_date,
            "region": "8",
            "county": county,
            "bin": single_row_values["bin"],
            "feature_carried": single_row_values["feature_carried"],
            "feature_crossed": single_row_values["feature_crossed"],
            "access": single_row_values["access"],
            "town": single_row_values["town"],
            "lane_closed": wztc(single_row_values["access"]),
        }
        for scheduled_date in scheduled_dates:
            entries.append({**base, "scheduled_date": scheduled_date})
    return entries


# TODO: implement input methods
# - Excel file upload
# - Google Sheets import
# - Google Forms integration
# - LangExtract / text box input
