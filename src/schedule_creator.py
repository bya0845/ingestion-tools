from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path

from openpyxl.styles import Alignment

from classes import BaseCreator

logger = getLogger(__name__)


@dataclass
class ScheduleCreator(BaseCreator):
    inspection_data: list[dict[str, str | int | datetime]] = field(default_factory=list)

    def initialize_inspection_data(
        self, data: list[dict[str, str | int | datetime]]
    ) -> None:
        if self.worksheet is None:
            raise RuntimeError("Worksheet not initialized")
        self.inspection_data = data
        self._populate_inspection_data()

    def _populate_inspection_data(self) -> None:
        if self.worksheet is None:
            raise RuntimeError("Worksheet not initialized")
        ws = self.worksheet
        header_row = 24
        for row_idx, record in enumerate(self.inspection_data, header_row + 1):
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
                cell.font = self.styles.table_font
                cell.alignment = Alignment(horizontal="center")
                cell.border = self.styles.thin_border
                if col in [2, 3] and isinstance(value, datetime):
                    cell.number_format = "mm/dd/yy"

        last_data_row = header_row + len(self.inspection_data)
        for row_idx in range(last_data_row + 1, header_row + 125):
            for col in range(1, 12):
                cell = ws.cell(row=row_idx, column=col)
                cell.border = self.styles.thin_border

    @staticmethod
    def generate_weekly_schedules(
        start_date: datetime,
        end_date: datetime,
        sample_data: list[dict[str, str | int | datetime]] | None = None,
        output_dir: Path | None = None,
    ) -> list[Path]:
        logger.info("Generating weekly schedules from %s to %s", start_date, end_date)
        if output_dir is None:
            output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        start_sunday = BaseCreator.get_sunday(start_date)
        end_sunday = BaseCreator.get_sunday(end_date)

        paths = []
        current_sunday = start_sunday
        while current_sunday <= end_sunday:
            filename = f"schedule_{current_sunday.strftime('%Y%m%d')}.xlsx"
            creator = ScheduleCreator(week_start=current_sunday)
            if sample_data:
                creator.initialize_inspection_data(sample_data)
            path = creator.save(filename)
            paths.append(path)
            logger.info(
                "Created schedule for week of %s", current_sunday.strftime("%m/%d/%Y")
            )
            current_sunday += timedelta(days=7)

        logger.info("Generated %d schedules", len(paths))
        return paths


def create_schedule(
    output_path: str, week_start: datetime, data: list[dict[str, str | int | datetime]]
) -> Path:
    creator = ScheduleCreator(week_start=week_start)
    creator.initialize_inspection_data(data)
    return creator.save(output_path)


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

    path = create_schedule("schedule1.xlsx", datetime(2025, 11, 9), sample_data)
    print(f"Schedule created: {path}")

    paths = ScheduleCreator.generate_weekly_schedules(
        start_date=datetime(2025, 11, 1),
        end_date=datetime(2025, 11, 30),
        sample_data=sample_data,
    )
    print(f"Generated {len(paths)} weekly schedules")
