from django.db import models


class Region(models.Model):
    """A NYSDOT inspection region."""

    number = models.IntegerField(unique=True)

    def __str__(self) -> str:
        return f"Region {self.number}"


class County(models.Model):
    """A county within a NYSDOT region."""

    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="counties", null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = "counties"
