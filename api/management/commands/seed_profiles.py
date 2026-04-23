import json
from django.core.management.base import BaseCommand
from api.models import Profile


class Command(BaseCommand):
    help = "Seed database with profile data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing profiles before seeding"
        )

    def handle(self, *args, **kwargs):

        reset = kwargs["reset"]

        if reset:
            self.stdout.write(self.style.WARNING("Deleting existing profiles..."))
            Profile.objects.all().delete()

        file_path = "seed_profiles.json"

        with open(file_path, "r") as file:
            data = json.load(file)

        # extract list properly
        records = data.get("profiles", [])

        created_count = 0
        existing_count = 0

        for record in records:
            # prevents duplicate
            name = record.get("name", "").lower()

            obj, created = Profile.objects.get_or_create(
                name=name,
                defaults={
                    "gender": record.get("gender"),
                    "gender_probability": record.get("gender_probability"),
                    "age": record.get("age"),
                    "age_group": record.get("age_group"),
                    "country_id": record.get("country_id"),
                    "country_name": record.get("country_name"),
                    "country_probability": record.get("country_probability"),
                }
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding complete: {created_count} created, {existing_count} skipped"
            )
        )