from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from logging import getLogger, DEBUG, basicConfig
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.worksheet import Worksheet

from src.utils import get_sunday

basicConfig(level=DEBUG)
logger = getLogger(__name__)


@dataclass
class BaseCreator:
    """Base class for initializing generic spreadsheet with borders and styling."""

    title: str | None = None
    workbook: Workbook = field(default_factory=Workbook)
    worksheet: Worksheet | None = field(init=False, default=None)
    week_start: datetime | None = None
    project_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    team_name: str = "Chen"
    output_dir_override: Path | None = None
    region: str = "8"
    sheet_title: str = field(init=False)
    default_filename: str = field(init=False)

    def __post_init__(self):
        if not self.title:
            self.title = "Bridge Inspection Weekly Schedule"
        if not self.week_start:
            self.week_start = get_sunday()
        self.sheet_title = f"Region {self.region}"
        week_str = self.week_start.strftime("%-m-%-d-%y")
        self.default_filename = (
            f"{self.team_name} Region {self.region} Bridge Inspection"
            f" Weekly Schedule - Week of {week_str}.xlsx"
        )
        self._init_directories()
        self.initialize_workbook()

    def _init_directories(self) -> None:
        try:
            self.project_dir = Path(__file__).resolve().parent.parent
        except (NameError, OSError) as e:
            logger.error(f"Failed to resolve project directory: {e}")
            self.project_dir = Path.cwd()
        self.output_dir = (
            self.output_dir_override
            if self.output_dir_override
            else self.project_dir / "output"
        )

    def initialize_workbook(self) -> None:
        """Initializes the workbook worksheet and dimensions."""
        logger.info("Initializing workbook")
        ws = self.workbook.active
        if ws is None:
            raise RuntimeError("Failed to create worksheet")
        ws.title = self.sheet_title
        self.worksheet = ws
        logger.debug("Worksheet created: %s", ws.title)
        self.initialize_dimensions()
        logger.info("Workbook initialization complete")

    def style_cell(
        self,
        row: int,
        col: int,
        value: str,
        font: Font,
        alignment: Alignment | None = None,
    ) -> None:
        """Writes a value to a cell and applies font and optional alignment."""
        if self.worksheet is None:
            raise RuntimeError("Worksheet not initialized")
        cell = self.worksheet.cell(row=row, column=col, value=value)
        cell.font = font
        if alignment:
            cell.alignment = alignment

    def initialize_dimensions(self) -> None:
        """Applies dimensions and styling to the worksheet. Override in subclasses."""
        pass

    def save(self, filename: str | None = None) -> Path:
        """Saves the workbook to the output directory and returns the file path."""
        if filename is None:
            filename = self.default_filename
        output_path = self.output_dir / filename
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Permission denied creating directory: {e}")
            raise
        except OSError as e:
            logger.error(f"Failed to create directory: {e}")
            raise

        try:
            self.workbook.save(output_path)
            logger.info(f"Workbook saved: {output_path}")
        except PermissionError as e:
            logger.error(f"Permission denied saving file: {e}")
            raise
        except OSError as e:
            logger.error(f"Failed to save workbook: {e}")
            raise
        return output_path

    def to_bytes(self) -> bytes:
        """Returns the workbook content as bytes without writing to disk."""
        buf = BytesIO()
        self.workbook.save(buf)
        return buf.getvalue()


def create_sample_workbook() -> Path:
    """Creates an empty sample schedule workbook using DB-backed contact and team data."""
    creator = BaseCreator()
    return creator.save("sample_schedule.xlsx")
