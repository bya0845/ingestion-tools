from django.db import models


class Employer(models.Model):
    """A firm that employs inspection teams."""

    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")

    def __str__(self) -> str:
        return self.name


class Team(models.Model):
    """An inspection team with a leader, ATL, employer, and contact number."""

    team_leader = models.CharField(max_length=100)
    atl = models.CharField(max_length=100)
    employer = models.ForeignKey(Employer, on_delete=models.PROTECT, related_name="teams")
    phone = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.employer}: {self.team_leader}, Team Leader; {self.atl}, ATL"


class Personnel(models.Model):
    """A project contact with name, role, and phone numbers."""

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    office_phone = models.CharField(max_length=20, blank=True, default="")
    cell_phone = models.CharField(max_length=20, blank=True, default="")

    def __str__(self) -> str:
        return f"{self.name} - {self.role}"
