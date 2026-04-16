"""Serializer to format output and validate input."""
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Full serializer for Profile model.

    Used for:
    - Creating a profile response (POST/api/profiles)
    - Retrieving a single profile (GET/api/profiles/{id})
    """
    class Meta:
        model = Profile
        fields = "__all__"

    def validate_name(self, value):
        """
        Validate name input before processing.
        """

        if not value:
            raise serializers.ValidationError("Name cannot be empty")

        if not isinstance(value, str):
            raise serializers.ValidationError("Name must be a string")

        value = value.strip().lower()

        # Only allow alphabetic names (no numbers/symbols)
        if not re.match(r"^[a-zA-Z]+$", value):
            raise serializers.ValidationError(
                "Name must contain only alphabetic characters"
            )

        return value

class ProfileListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing profiles.

    Used for:
    - GET /api/profiles (list endpoint with optional filtering)
    """
    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "gender",
            "age",
            "age_group",
            "country_id",
        ]