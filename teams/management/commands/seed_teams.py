from django.core.management.base import BaseCommand
from teams.models import Employer, Team, Personnel
from src.constants import REGION8_TEAMS, CONTACTS

EMPLOYER_NAMES = {"WSP USA", "South Col", "Lu Eng"}


class Command(BaseCommand):
    """Seed the database with initial employers, teams, and personnel from constants."""

    def handle(self, *args, **options):
        for name in EMPLOYER_NAMES:
            Employer.objects.get_or_create(name=name)
        self.stdout.write("Employers seeded.")

        for t in REGION8_TEAMS:
            employer = Employer.objects.get(name=t.employer)
            Team.objects.get_or_create(
                team_leader=t.team_leader,
                defaults={
                    "atl": t.atl,
                    "employer": employer,
                    "phone": t.phone,
                },
            )
        self.stdout.write("Teams seeded.")

        for p in CONTACTS:
            Personnel.objects.get_or_create(
                name=p.name,
                defaults={
                    "role": p.role,
                    "office_phone": p.office_phone,
                    "cell_phone": p.cell_phone,
                },
            )
        self.stdout.write("Personnel seeded.")
