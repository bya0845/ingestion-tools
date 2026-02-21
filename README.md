# WSP USA — NYSDOT Region 8 Bridge Inspection Schedule Generator

Django + PostgreSQL + React web app for generating weekly bridge inspection schedule spreadsheets (`.xlsx`) for NYSDOT Region 8.

## What it does

1. User pastes rows copied from the master Excel spreadsheet into the web form.
2. The app parses the tab-separated data, auto-detects the column layout, and shows an editable preview table.
3. Cells in the preview can be edited before generating.
4. Clicking **Generate Schedules** groups entries by week, builds one `.xlsx` file per week using `openpyxl`, and serves them as a browser download (single file or zip for multiple weeks).
5. An optional output directory can be entered to also save files server-side.

## Supported booked-access date formats

- Single date: `10/14/25` or `10/14` (defaults to 2025)
- Multiple dates: `10/14/25 & 10/25/25` → one row per date
- Date range: `10/14/25 to 10/16/25` → one row per day

## Stack

**Backend:**
- Django 6 / Django REST Framework / PostgreSQL 16
- `uv` package manager
- `openpyxl` for Excel generation
- `pydantic` for entry validation

**Frontend:**
- React 19
- React Router
- Vite (dev server + build tool)

## Development Setup

This is a monorepo with separate `backend/` (Django) and `frontend/` (React) directories.

### Backend

```bash
cd backend
uv sync                                    # Install dependencies
uv pip install djangorestframework django-cors-headers  # If not auto-installed
python manage.py migrate                   # Apply migrations
python manage.py runserver                 # Start dev server at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install                                # Install dependencies
npm run dev                                # Start dev server at http://localhost:5173
```

### Running Both Together

In separate terminals:
```bash
# Terminal 1: Backend
cd backend && python manage.py runserver

# Terminal 2: Frontend
cd frontend && npm run dev
```

Access the application at http://localhost:5173

## Quick Start

### 1. Start PostgreSQL Database

```bash
# PostgreSQL must be running on localhost:5432
# Configure database settings in backend/.env/.env

# If using Ubuntu/Linux:
sudo systemctl start postgresql

# Or if using Docker:
docker run --name postgres -e POSTGRES_PASSWORD=eE0232>v -p 5432:5432 -d postgres:16
```

### 2. Apply Database Migrations

```bash
cd backend
python manage.py migrate
```

### 3. Create Superuser (Admin Login)

```bash
cd backend
python manage.py createsuperuser
# Follow prompts to create username, email, password
```

### 4. Seed Initial Data

```bash
cd backend
python manage.py seed_inspections    # Creates Region 8 and counties
python manage.py seed_teams          # Creates employers, teams, and personnel
```

### 5. Start Backend and Frontend

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### 6. Access Application

- **Admin Panel:** http://localhost:8000/admin
  - Username/password: your superuser credentials
  - Manage teams, personnel, employers, regions, counties

- **Application:** http://localhost:5173
  - Generate inspection schedules

## API Endpoints

### Admin
- `GET /admin/` — Django admin interface (requires superuser login)

### Teams
- `GET /api/teams/` — List all teams (returns `[{value, label}]` for dropdowns)

### Inspections
- `POST /api/inspections/preview/` — Parse TSV data and return preview entries
  - Body: `{raw_tsv: string}`
  - Returns: `{entries: array, count: number}`

- `POST /api/inspections/schedule/` — Generate schedule Excel files
  - Body: `{team_name: string, entries_json: string, output_dir: string}`
  - Returns: Excel file (single) or ZIP archive (multiple weeks)

### Management Commands (CLI)
```bash
cd backend
python manage.py seed_inspections   # Populate Region 8 and counties
python manage.py seed_teams         # Populate employers, teams, personnel
python manage.py generate_sample    # Generate sample schedule to output/
```

## Frontend Routes

| Route          | Page                      |
|----------------|---------------------------|
| `/`            | Home                      |
| `/schedule`    | Generate Schedule         |
| `/daily-logs`  | Generate Daily Logs       |
| `/bat-survey`  | Generate Bat Survey Forms |
| `/801-sketch`  | Generate 801 Sketch       |

## Apps

| App           | Purpose                                             |
| ------------- | --------------------------------------------------- |
| `inspections` | API endpoints for schedule generation               |
| `documents`   | Excel workbook creators and entry schemas           |
| `teams`       | Inspection team and personnel models; seed commands |

## Database Schema

The `teams` app manages inspection teams and personnel:

### Employer
```
id (PK)  | name          | address   | phone
---------|---------------|-----------|----------
1        | WSP USA       | ...       | ...
2        | South Col     | ...       | ...
3        | Lu Eng        | ...       | ...
```

### Team
```
id (PK)  | team_leader | atl   | employer_id (FK) | phone
---------|-------------|-------|------------------|----------
1        | John        | Jane  | 1                | 555-0001
2        | Bob         | Alice | 2                | 555-0002
```

### Personnel
```
id (PK)  | name     | role      | office_phone | cell_phone
---------|----------|-----------|--------------|----------
1        | John Doe | Inspector | 555-1234     | 555-5678
2        | Jane Dea | Supervisor| 555-1235     | 555-5679
```

**Relationships:**
- Each `Team` belongs to one `Employer` (via `employer_id` foreign key)
- `Personnel` are independent contacts used in schedules

## Seed commands

```bash
python manage.py seed_inspections   # counties and region
python manage.py seed_teams         # inspection teams and personnel contacts
python manage.py generate_sample    # writes a sample schedule to output/
```
