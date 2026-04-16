"""Models for data storage of each profile"""
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
    sample_size = models.IntegerField()

    age = models.IntegerField()
    age_group = models.CharField(max_length=20)

    country_id = models.CharField(max_length=10)
    country_probability = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Normalize name to lowercase before saving."""
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name