# WSP USA — NYSDOT Region 8 Bridge Inspection Schedule Generator

Django + PostgreSQL web app for generating weekly bridge inspection schedule spreadsheets (`.xlsx`) for NYSDOT Region 8.

## What it does

1. User pastes rows copied from the master Excel spreadsheet into the web form at `/inspections/schedule/`.
2. The app parses the tab-separated data, auto-detects the column layout, and shows an editable preview table.
3. Cells in the preview can be edited before generating.
4. Clicking **Generate Schedules** groups entries by week, builds one `.xlsx` file per week using `openpyxl`, and serves them as a browser download (single file or zip for multiple weeks).
5. An optional output directory can be entered to also save files server-side.

## Supported booked-access date formats

- Single date: `10/14/25`
- Multiple dates: `10/14/25 & 10/25/25` → one row per date
- Date range: `10/14/25 to 10/16/25` → one row per day

## Stack

- Django 6 / PostgreSQL 16
- `uv` package manager
- `openpyxl` for Excel generation
- `pydantic` for entry validation

## Apps

| App           | Purpose                                             |
| ------------- | --------------------------------------------------- |
| `inspections` | Schedule generation view and URL routing            |
| `documents`   | Excel workbook creators and entry schemas           |
| `teams`       | Inspection team and personnel models; seed commands |

## Seed commands

```bash
python manage.py seed_inspections   # counties and region
python manage.py seed_teams         # inspection teams and personnel contacts
python manage.py generate_sample    # writes a sample schedule to output/
```
