from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        AGENT = "agent", "Support agent"

    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="users",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
