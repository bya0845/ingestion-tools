from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


class Employer(StrEnum):
    WSP_USA = "WSP USA"
    SOUTH_COL = "South Col"
    LU_ENG = "Lu Eng"


@dataclass(frozen=True)
class Team:
    """Represents an inspection team with a leader, ATL, employer, and contact number."""

    team_leader: str
    atl: str
    employer: Employer
    phone: str

    def __str__(self) -> str:
        return f"{self.employer}: {self.team_leader}, Team Leader; {self.atl}, ATL"


COUNTY_MAP: MappingProxyType[int, str] = MappingProxyType(
    {
        1: "Columbia",
        2: "Dutchess",
        3: "Orange",
        4: "Putnam",
        5: "Rockland",
        6: "Ulster",
        7: "Westchester",
    }
)


@dataclass(frozen=True)
class Personnel:
    name: str
    role: str
    office_phone: str
    cell_phone: str


CONTACTS: tuple[Personnel, ...] = (
    Personnel(
        name="Salvatore Iodice",
        role="Project Manager",
        office_phone="",
        cell_phone="(917) 763-2519",
    ),
    Personnel(
        name="Amy Hutcheson",
        role="Asst. Project Manager",
        office_phone="(914) 449-9038",
        cell_phone="917-902-0186",
    ),
    Personnel(
        name="Karen Tomapat",
        role="Scheduling/Office Assistant",
        office_phone="(914) 449-9144",
        cell_phone="845-283-0224",
    ),
    Personnel(
        name="Stephanie Santiago",
        role="Office Assistant",
        office_phone="",
        cell_phone="917-509-0650",
    ),
    Personnel(
        name="Stacie Diamond",
        role="Asst. Project Manager",
        office_phone="(914) 449-9136",
        cell_phone="845-642-7036",
    ),
    Personnel(
        name="Robert Seeley",
        role="Quality Control",
        office_phone="",
        cell_phone="(914) 262-2766",
    ),
)

REGION8_TEAMS: tuple[Team, ...] = (
    Team(
        employer=Employer.WSP_USA,
        team_leader="Tom Barrell",
        atl="Nick Diflorio",
        phone="518-330-8841",
    ),
    Team(
        employer=Employer.WSP_USA,
        team_leader="Ben Kolesnik",
        atl="Frank Fraser",
        phone="845-596-7106",
    ),
    Team(
        employer=Employer.WSP_USA,
        team_leader="Oleg Shyputa",
        atl="Dan Rivie",
        phone="646-387-3354",
    ),
    Team(
        employer=Employer.WSP_USA,
        team_leader="Matt Bacon",
        atl="Nick Mendola",
        phone="774-239-9739",
    ),
    Team(
        employer=Employer.WSP_USA,
        team_leader="Kevin Milligan",
        atl="Christian Flores",
        phone="212-784-0037",
    ),
    Team(
        employer=Employer.WSP_USA,
        team_leader="Dan Hadden",
        atl="Dionis Demukaj",
        phone="845-661-6525",
    ),
    Team(
        employer=Employer.SOUTH_COL,
        team_leader="Shuangbi Chen",
        atl="Bo Lun Yang",
        phone="518-955-1990",
    ),
    Team(
        employer=Employer.LU_ENG,
        team_leader="Laura Fulford",
        atl="Ruzen Shafir",
        phone="518-577-7117",
    ),
)
