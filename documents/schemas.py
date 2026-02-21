from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class InspectionEntry(BaseModel):
    """A single bridge inspection entry for a weekly schedule row."""

    team: str
    scheduled_date: datetime
    due_date: datetime | None = None
    region: str
    county: str
    bin: str
    feature_carried: str
    feature_crossed: str
    access: str
    town: str
    lane_closed: Literal["Y", "N"]
