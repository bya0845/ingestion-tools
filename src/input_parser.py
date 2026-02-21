from datetime import datetime, timedelta

from inspections.models import County


LANE_CLOSED_TRIGGERS = {"WZTC", "UB60", "UB50", "UB40"}

# Column offsets relative to the BIN column in the master spreadsheet TSV.
# County (Cty) is at absolute col 0 when present; BIN follows immediately after.
# If Cty is omitted when copying, BIN lands at col 0 and all offsets shift left by 1.
PASTE_COLUMN_OFFSETS: dict[int, str] = {
    0: "bin",
    1: "feature_carried",
    2: "feature_crossed",
    5: "due_date",
    14: "access",
    15: "scheduled_date",
    17: "team",
    18: "town",
}


def parse_scheduled_dates(raw: str) -> list[datetime]:
    """Parses a booked-access date string into a list of datetimes.

    Handles single dates ("10/14/25"), ampersand-separated dates ("10/14/25 & 10/25/25"),
    and inclusive ranges ("10/14/25 to 10/16/25"). Silently skips unparseable tokens.
    """
    raw = raw.strip()
    raw_lower = raw.lower()

    # Range: "start to end" — expand every day inclusive
    if " to " in raw_lower:
        idx = raw_lower.index(" to ")
        start_str = raw[:idx].strip()
        end_str = raw[idx + 4:].strip()
        try:
            start = datetime.strptime(start_str, "%m/%d/%y")
            end = datetime.strptime(end_str, "%m/%d/%y")
            dates = []
            current = start
            while current <= end:
                dates.append(current)
                current += timedelta(days=1)
            return dates
        except ValueError:
            return []

    # Ampersand-separated: one entry per date token
    if "&" in raw:
        dates = []
        for part in raw.split("&"):
            try:
                dates.append(datetime.strptime(part.strip(), "%m/%d/%y"))
            except ValueError:
                pass
        return dates

    # Single date
    try:
        return [datetime.strptime(raw, "%m/%d/%y")]
    except ValueError:
        return []


def lane_closed(access: str | None) -> str:
    """Returns Y if access type requires lane closure, N otherwise."""
    if not access:
        return "N"
    return "Y" if any(t in access for t in LANE_CLOSED_TRIGGERS) else "N"


def get_week_start(date: datetime) -> datetime:
    """Returns the Sunday that starts the week containing date."""
    return date - timedelta(days=(date.weekday() + 1) % 7)


def get_county_name(county_id: int) -> str:
    """Returns county name from the database by ID."""
    try:
        return County.objects.get(id=county_id).name
    except County.DoesNotExist:
        return ""


def parse_entries_from_table(raw_entries: list[dict]) -> list[dict]:
    """Parses table-cell entry dicts (from the editable preview table) into inspection entry dicts.

    Accepts dates in m/d/Y or m/d/y format. Skips rows missing a bin or valid scheduled date.
    """
    entries = []
    for e in raw_entries:
        bin_val = e.get("bin", "").strip()
        if not bin_val:
            continue
        scheduled_date = None
        for fmt in ("%m/%d/%Y", "%m/%d/%y"):
            try:
                scheduled_date = datetime.strptime(e.get("scheduled_date", "").strip(), fmt)
                break
            except ValueError:
                pass
        if scheduled_date is None:
            continue
        due_date = None
        due_raw = e.get("due_date", "").strip()
        if due_raw and due_raw != "-":
            for fmt in ("%m/%d/%Y", "%m/%d/%y"):
                try:
                    due_date = datetime.strptime(due_raw, fmt)
                    break
                except ValueError:
                    pass
        lc = e.get("lane_closed", "N").strip().upper()
        entries.append({
            "team": "",
            "scheduled_date": scheduled_date,
            "due_date": due_date,
            "region": "8",
            "county": e.get("county", "").strip(),
            "bin": bin_val,
            "feature_carried": e.get("feature_carried", "").strip(),
            "feature_crossed": e.get("feature_crossed", "").strip(),
            "access": e.get("access", "").strip(),
            "town": e.get("town", "").strip(),
            "lane_closed": lc if lc in ("Y", "N") else "N",
        })
    return entries


def parse_tsv(raw: str, year: int | None = None) -> list[dict]:
    """Parses tab-separated text pasted from Excel into a list of inspection entry dicts.

    Handles two layouts automatically:
    - 20-column: Cty at col 0, BIN at col 1 (county ID is a 1-2 digit integer)
    - 19-column: BIN at col 0, no county column

    Skips rows with no BIN, no scheduled date, or an unparseable scheduled date.
    Due date is expected in MMDD format (e.g. 1107 = Nov 7); year defaults to current year.
    """
    if year is None:
        year = datetime.now().year
    entries = []
    for line in raw.splitlines():
        cols = line.split("\t")
        first = cols[0].strip()
        # A 1-2 digit integer in col 0 is a county ID; anything else means county col is absent.
        if first.isdigit() and int(first) < 100:
            county = get_county_name(int(first))
            c = 1  # BIN starts at col 1
        else:
            county = ""
            c = 0  # BIN starts at col 0
        if len(cols) < c + 16:
            continue
        bin_val = cols[c].strip()
        if not bin_val:
            continue
        sched_raw = cols[c + 15].strip()
        if not sched_raw:
            continue
        scheduled_dates = parse_scheduled_dates(sched_raw)
        if not scheduled_dates:
            continue
        due_raw = cols[c + 5].strip() if c + 5 < len(cols) else ""
        due_date = None
        if len(due_raw) == 4 and due_raw.isdigit():
            try:
                due_date = datetime(year, int(due_raw[:2]), int(due_raw[2:]))
            except ValueError:
                pass
        access = cols[c + 14].strip() if c + 14 < len(cols) else ""
        base = {
            "team": cols[c + 17].strip() if c + 17 < len(cols) else "",
            "due_date": due_date,
            "region": "8",
            "county": county,
            "bin": bin_val,
            "feature_carried": cols[c + 1].strip() if c + 1 < len(cols) else "",
            "feature_crossed": cols[c + 2].strip() if c + 2 < len(cols) else "",
            "access": access,
            "town": cols[c + 18].strip() if c + 18 < len(cols) else "",
            "lane_closed": lane_closed(access),
        }
        for scheduled_date in scheduled_dates:
            entries.append({**base, "scheduled_date": scheduled_date})
    return entries


# TODO: implement input methods
# - Excel file upload
# - Google Sheets import
# - Google Forms integration
# - LangExtract / text box input
