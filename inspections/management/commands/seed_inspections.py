from django.core.management.base import BaseCommand
from inspections.models import County, Region
from src.constants import COUNTY_MAP


class Command(BaseCommand):
    """Seed the database with initial region and county data from constants."""

    def handle(self, *args, **options) -> None:
        region8, _ = Region.objects.get_or_create(number=8)

        for county_id, name in COUNTY_MAP.items():
            County.objects.get_or_create(
                id=county_id,
                defaults={"name": name, "region": region8},
            )

        self.stdout.write("Regions and counties seeded.")
