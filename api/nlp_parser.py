import re
from iso3166 import countries

COUNTRY_MAP = {c.name: c.alpha2 for c in countries}
    
def parse_query(q):
    q = q.lower()

    filters = {}

    # gender
    if re.search(r"\bfemale(s)?\b", q):
        filters["gender"] = "female"

    elif re.search(r"\bmale(s)?\b", q):
        filters["gender"] = "male"

    # age group
    if "child" in q:
        filters["age_group"] = "child"
    elif "teenager" in q:
        filters["age_group"] = "teenager"
    elif "adult" in q:
        filters["age_group"] = "adult"
    elif "senior" in q:
        filters["age_group"] = "senior"

    # young
    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # above age
    match = re.search(r"above (\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))

    # country
    for country, code in COUNTRY_MAP.items():
        if country in q:
            filters["country_id"] = code

    if not filters:
        return None

    return filters