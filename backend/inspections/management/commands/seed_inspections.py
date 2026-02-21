import logging

from django.core.management.base import BaseCommand

from inspections.models import County, Region
from src.constants import COUNTY_MAP

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Seed the database with initial region and county data from constants."""

    def handle(self, *args, **options) -> None:
        region8, _ = Region.objects.get_or_create(number=8)
        logger.info("Region 8 created/retrieved.")

        for county_id, name in COUNTY_MAP.items():
            County.objects.get_or_create(
                id=county_id,
                defaults={"name": name, "region": region8},
            )

        logger.info("Regions and counties seeded.")
