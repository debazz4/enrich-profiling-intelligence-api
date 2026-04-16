"""Tests for all API endpoints."""
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .models import Profile

MOCK_GENDER = {
    "gender": "female",
    "probability": 0.99,
    "count": 1000
}

MOCK_AGE = {
    "age": 30
}

MOCK_COUNTRY = {
    "country": [
        {"country_id": "NG", "probability": 0.85},
        {"country_id": "US", "probability": 0.15}
    ]
}

class ProfileAPITest(APITestCase):

    @patch("api.services.requests.get")
    def test_create_profile_success(self, mock_get):
        # Mock API responses
        mock_get.side_effect = [
            MockResponse(MOCK_GENDER),
            MockResponse(MOCK_AGE),
            MockResponse(MOCK_COUNTRY),
        ]

        response = self.client.post("/api/profiles", {"name": "Ella"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["data"]["name"], "ella")
        self.assertEqual(response.data["data"]["age_group"], "adult")

    @patch("api.services.requests.get")
    def test_idempotency(self, mock_get):
        mock_get.side_effect = [
            MockResponse(MOCK_GENDER),
            MockResponse(MOCK_AGE),
            MockResponse(MOCK_COUNTRY),
        ]

        # First request
        self.client.post("/api/profiles", {"name": "Ella"}, format="json")

        # Second request
        response = self.client.post("/api/profiles", {"name": "Ella"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Profile already exists", response.data["message"])
        self.assertEqual(Profile.objects.count(), 1)

    def test_get_profile(self):
        profile = Profile.objects.create(
            name="ella",
            gender="female",
            gender_probability=0.99,
            sample_size=1000,
            age=30,
            age_group="adult",
            country_id="NG",
            country_probability=0.85,
        )

        response = self.client.get(f"/api/profiles/{profile.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["name"], "ella")

    def test_filter_profiles(self):
        Profile.objects.create(
            name="ella",
            gender="female",
            gender_probability=0.99,
            sample_size=1000,
            age=30,
            age_group="adult",
            country_id="NG",
            country_probability=0.85,
        )

        Profile.objects.create(
            name="john",
            gender="male",
            gender_probability=0.99,
            sample_size=1000,
            age=25,
            age_group="adult",
            country_id="US",
            country_probability=0.80,
        )

        response = self.client.get("/api/profiles?gender=female")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
    
    def test_delete_profile(self):
        profile = Profile.objects.create(
            name="ella",
            gender="female",
            gender_probability=0.99,
            sample_size=1000,
            age=30,
            age_group="adult",
            country_id="NG",
            country_probability=0.85,
        )

        response = self.client.delete(f"/api/profiles/{profile.id}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Profile.objects.count(), 0)

    def test_missing_name(self):
        response = self.client.post("/api/profiles", {}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_invalid_name_type(self):
        response = self.client.post("/api/profiles", {"name": 123}, format="json")

        self.assertEqual(response.status_code, 422)
    
    @patch("api.services.requests.get")
    def test_genderize_failure(self, mock_get):
        mock_get.side_effect = [
            MockResponse({"gender": None, "count": 0}),
            MockResponse(MOCK_AGE),
            MockResponse(MOCK_COUNTRY),
        ]

        response = self.client.post("/api/profiles", {"name": "Ella"}, format="json")

        self.assertEqual(response.status_code, 502)
        self.assertIn("Genderize", response.data["message"])
    
    def test_case_insensitive_name(self):
        Profile.objects.create(
            name="ella",
            gender="female",
            gender_probability=0.99,
            sample_size=1000,
            age=30,
            age_group="adult",
            country_id="NG",
            country_probability=0.85,
        )

        response = self.client.post("/api/profiles", {"name": "ELLA"}, format="json")

        self.assertEqual(response.status_code, 200)
class MockResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data