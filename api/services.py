"""Services for handling data enrichment for profiles."""
import requests

from iso3166 import countries


class ExternalAPIError(Exception):
    """Custom exception class for error handling."""
    def __init__(self, api_name):
        self.api_name = api_name


def get_age_group(age):
    """Handles Age segregation based on the age."""
    if age <= 12:
        return "child"
    elif age <= 19:
        return "teenager"
    elif age <= 59:
        return "adult"
    return "senior"

def get_country_name(alpha2):
    """Country name helper."""
    country = countries.get(alpha2).name
    return country if country else alpha2

def enrich_profile(name):
    try:
        # Call APIs with timeouts to prevent hanging
        gender_data = requests.get(
            f"https://api.genderize.io?name={name}",
            timeout=5
        )
        age_data = requests.get(
            f"https://api.agify.io?name={name}",
            timeout=5
        )
        country_data = requests.get(
            f"https://api.nationalize.io?name={name}",
            timeout=5
        )

        # Prevents invalid JSON crashes
        gender_data.raise_for_status()
        age_data.raise_for_status()
        country_data.raise_for_status()

        gender_res = gender_data.json()
        age_res = age_data.json()
        country_res = country_data.json()

    except Exception:
        # Any external failure
        raise ExternalAPIError("External API")
    
    # Call APIs
    # gender_res = requests.get(f"https://api.genderize.io?name={name}").json()
    # age_res = requests.get(f"https://api.agify.io?name={name}").json()
    # country_res = requests.get(f"https://api.nationalize.io?name={name}").json()

    # Gender validation
    if gender_res.get("gender") is None or gender_res.get("count") == 0:
        raise ExternalAPIError("Genderize")

    # Age validation
    if age_res.get("age") is None:
        raise ExternalAPIError("Agify")

    # Nationalize validation
    if not country_res.get("country"):
        raise ExternalAPIError("Nationalize")

    # prcess comparism based on probability
    top_country = max(
        country_res["country"],
        key=lambda x: x["probability"]
    )

    country_id = top_country["country_id"]

    return {
        "gender": gender_res["gender"],
        "gender_probability": gender_res["probability"],
        "sample_size": gender_res["count"],
        "age": age_res["age"],
        "age_group": get_age_group(age_res["age"]),
        "country_id": top_country["country_id"],
        "country_name": get_country_name(country_id),
        "country_probability": top_country["probability"],
    }