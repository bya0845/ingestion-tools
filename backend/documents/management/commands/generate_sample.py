from django.core.management.base import BaseCommand
from documents.templates.base_doc import create_sample_workbook


class Command(BaseCommand):
    """Generates a sample schedule workbook to verify DB-backed team and contact data."""

    def handle(self, *args, **options) -> None:
        path = create_sample_workbook()
        self.stdout.write(f"Sample workbook created: {path}")
