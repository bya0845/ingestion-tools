from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from datetime import datetime, timedelta
from pathlib import Path

thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

title_font = Font(name="Arial", size=9, bold=True)
normal_font = Font(name="Arial", size=9)
table_font = Font(name="Arial", size=10)


def create_schedule(output_path: str, week_start: datetime, data: list[dict]):
    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise RuntimeError("Failed to create worksheet")
    ws.title = "Region 8"

    column_widths = {
        "A": 14.1,
        "B": 17.1,
        "C": 13,
        "D": 13.6,
        "E": 17.1,
        "F": 16.1,
        "G": 29.7,
        "H": 34,
        "I": 25.5,
        "J": 20.6,
        "K": 12.1,
        "L": 13,
        "M": 13,
        "N": 13,
        "O": 13,
        "P": 13,
        "Q": 13,
        "R": 13,
        "S": 13,
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    for row in range(1, 23):
        ws.row_dimensions[row].height = 12.75
    ws.row_dimensions[23].height = 4.5
    ws.row_dimensions[24].height = 30
    for row in range(25, 160):
        ws.row_dimensions[row].height = 15

    for row in range(1, 23):
        for col in range(1, 12):
            ws.cell(row=row, column=col).border = thin_border

    ws["A1"] = "WSP USA, INC."
    ws["A1"].font = title_font
    ws["A2"] = "NYSDOT 2025 Region 8 Bridge Inspection"
    ws["A2"].font = title_font
    ws["A3"] = "Contract No. D037877"
    ws["A3"].font = title_font

    ws["H1"] = "Inspection Schedule for week of:"
    ws["H1"].font = normal_font
    ws["I1"] = week_start
    ws["I1"].font = normal_font
    ws["J1"] = week_start + timedelta(days=6)
    ws["J1"].font = normal_font
    ws["I2"] = "(Sunday)"
    ws["I2"].font = normal_font
    ws["J2"] = "(Saturday)"
    ws["J2"].font = normal_font

    ws.merge_cells("G3:H3")
    ws.merge_cells("H1:I1")

    ws["A5"] = "Salvatore Iodice, Project Manager"
    ws["A5"].font = normal_font
    ws["A6"] = "Cell PH  (917) 763-2519"
    ws["A6"].font = normal_font

    ws["A8"] = "Amy Hutcheson, Asst. Project Manager"
    ws["A8"].font = normal_font
    ws["A9"] = "Office PH (914) 449-9038"
    ws["A9"].font = normal_font
    ws["C9"] = "Cell 917-902-0186"
    ws["C9"].font = normal_font

    ws["A11"] = "Karen Tomapat, Scheduling/Office Assistant"
    ws["A11"].font = normal_font
    ws["A12"] = "Office PH (914) 449-9144"
    ws["A12"].font = normal_font
    ws["C12"] = "Cell 845-283-0224"
    ws["C12"].font = normal_font

    ws.merge_cells("G7:H7")
    ws.merge_cells("G10:H10")

    ws["A14"] = "Stacie Diamond, Asst. Project Manager"
    ws["A14"].font = normal_font
    ws["A15"] = "Office PH (914) 449-9136"
    ws["A15"].font = normal_font
    ws["C15"] = "Cell 845-642-7036"
    ws["C15"].font = normal_font

    ws["A17"] = "Robert Seeley, Quality Control"
    ws["A17"].font = normal_font
    ws["A18"] = "Cell PH (914) 262-2766"
    ws["A18"].font = normal_font

    ws["G18"] = "Access Key:"
    ws["G18"].font = normal_font
    ws["H18"] = "W = Walking"
    ws["H18"].font = normal_font
    ws["G19"] = "SL = Step Ladder"
    ws["G19"].font = normal_font
    ws["G20"] = "EL = Extension Ladder"
    ws["G20"].font = normal_font
    ws["G21"] = "BT = Bucket Truck"
    ws["G21"].font = normal_font
    ws["G22"] = "UB = Under Bridge Unit"
    ws["G22"].font = normal_font

    ws["F5"] = "Inspection Teams:"
    ws["F5"].font = normal_font

    inspection_teams = [
        (4, "WSP USA: Tom Barrell, Team Leader; Nick Diflorio, ATL", "518-330-8841"),
        (5, "WSP USA: Ben Kolesnik, Team Leader; Frank Fraser, ATL", "845-596-7106"),
        (6, "WSP USA: Oleg Shyputa, Team Leader; Dan Rivie, ATL", "646-387-3354"),
        (7, "WSP USA: Matt Bacon, Team Leader; Nick Mendola, ATL", "774-239-9739"),
        (
            8,
            "WSP USA: Kevin Milligan, Team Leader; Christian Flores, ATL",
            "212-784-0037",
        ),
        (9, "WSP USA: Dan Hadden, Team Leader; Dionis Demukaj, ATL", "845-661-6525"),
        (10, "South Col: Shuangbi Chen, Team Leader; Bo Lun Yang, ATL", "518-955-1990"),
        (11, "Lu Eng: Laura Fulford, Team Leader; Ruzen Shafir, ATL", "518-577-7117"),
    ]
    for row, team_info, phone in inspection_teams:
        ws.cell(row=row, column=7, value=team_info).font = normal_font
        ws.cell(row=row, column=9, value=phone).font = normal_font

    ws.merge_cells("G4:H4")
    ws.merge_cells("G5:H5")
    ws.merge_cells("G6:H6")
    ws.merge_cells("G7:H7")
    ws.merge_cells("G8:H8")
    ws.merge_cells("G9:H9")
    ws.merge_cells("G10:H10")
    ws.merge_cells("G11:H11")

    headers = [
        "TEAM",
        "SCHEDULED DATE",
        "DUE DATE",
        "REGION",
        "COUNTY",
        "BIN",
        "FEATURE CARRIED",
        "FEATURE CROSSED",
        "ACCESS",
        "TOWN/LOC",
        "LANE CLOSED",
    ]

    header_row = 24
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col, value=header)
        cell.font = table_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin_border

    for row_idx, record in enumerate(data, header_row + 1):
        values = [
            record.get("team"),
            record.get("scheduled_date"),
            record.get("due_date"),
            record.get("region"),
            record.get("county"),
            record.get("bin"),
            record.get("feature_carried"),
            record.get("feature_crossed"),
            record.get("access"),
            record.get("town_loc"),
            record.get("lane_closed"),
        ]
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            cell.font = table_font
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border
            if col in [2, 3] and isinstance(value, datetime):
                cell.number_format = "mm/dd/yy"

    last_data_row = header_row + len(data)
    for row_idx in range(last_data_row + 1, header_row + 125):
        for col in range(1, 12):
            cell = ws.cell(row=row_idx, column=col)
            cell.border = thin_border

    output_file = Path(__file__).parent.parent / "output" / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_file)


if __name__ == "__main__":
    sample_data = [
        {
            "team": "Chen",
            "scheduled_date": datetime(2025, 11, 10),
            "due_date": datetime(2025, 12, 16),
            "region": 8,
            "county": "Ulster",
            "bin": 3347440,
            "feature_carried": "CAPE AVENUE",
            "feature_crossed": "BEER KILL",
            "access": "W, EL",
            "town_loc": "V. Ellenville",
            "lane_closed": "N",
        },
        {
            "team": "Chen",
            "scheduled_date": datetime(2025, 11, 10),
            "due_date": datetime(2025, 11, 29),
            "region": 8,
            "county": "Ulster",
            "bin": 1095450,
            "feature_carried": "209 209 86031052",
            "feature_crossed": "FANTINE KILL",
            "access": "W, EL",
            "town_loc": "V. Ellenville",
            "lane_closed": "N",
        },
    ]

    create_schedule("schedule1.xlsx", datetime(2025, 11, 9), sample_data)
    print("Schedule created: schedule1.xlsx")
