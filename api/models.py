"""Models for data storage of each profile"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid6 import uuid7


class Profile(models.Model):

    """
    Stores enriched profile data generated from external APIs.
    Ensures uniqueness of name for idempotent requests.
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.CharField(max_length=255, unique=True)

    gender = models.CharField(max_length=10)
    gender_probability = models.FloatField()

    age = models.IntegerField()
    age_group = models.CharField(max_length=20)

    country_id = models.CharField(max_length=2)
    country_name = models.CharField(max_length=255)
    country_probability = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Normalize name to lowercase before saving."""
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["gender"]),
            models.Index(fields=["country_id"]),
            models.Index(fields=["age"]),
            models.Index(fields=["age_group"]),
        ]
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("analyst", "Analyst"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="analyst")

    # IMPORTANT FIX: avoid clashes
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="api_user_groups",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="api_user_permissions",
        blank=True
    )