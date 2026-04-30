import re
from iso3166 import countries

COUNTRY_MAP = {c.name.lower(): c.alpha2 for c in countries}
    
def parse_gender(q, filters):
    q = q.lower()

    # handle combined case FIRST (important)
    if re.search(r"\bmale and female\b", q):
        return  # no gender filter

    if re.search(r"\bfemale(s)?\b", q):
        filters["gender"] = "female"
        return

    if re.search(r"\bmale(s)?\b", q):
        filters["gender"] = "male"

def parse_age(q, filters):

    # young = 16–24
    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24

    # teenagers
    if "teenager" in q or "teenagers" in q:
        filters["age_group"] = "teenager"

        match = re.search(r"above (\d+)", q)
        if match:
            filters["min_age"] = int(match.group(1))

    # adults
    if "adult" in q:
        filters["age_group"] = "adult"

    # above X
    match = re.search(r"above (\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))

    # below X
    match = re.search(r"below (\d+)", q)
    if match:
        filters["max_age"] = int(match.group(1))
        
    # country
def parse_country(q, filters):
    q = q.lower()

    for name, code in COUNTRY_MAP.items():
        if re.search(rf"\b{name}\b", q):
            filters["country_id"] = code
            return

def parse_query(q):
    filters = {}
    q = q.lower()

    parse_gender(q, filters)
    parse_age(q, filters)
    parse_country(q, filters)

    from .query_parser import validate_filters
    validate_filters(filters)

    return filters