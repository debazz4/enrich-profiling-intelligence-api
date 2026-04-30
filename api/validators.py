from rest_framework.response import Response
from rest_framework import status


def validate_query_params(params):
    allowed_sort_by = {"age", "created_at", "gender_probability"}
    allowed_order = {"asc", "desc"}
    allowed_gender = {"male", "female"}
    allowed_age_group = {"child", "teenager", "adult", "senior"}

    # sort validation
    if "sort_by" in params and params["sort_by"] not in allowed_sort_by:
        raise ValueError("Invalid query parameters")

    if "order" in params and params["order"] not in allowed_order:
        raise ValueError("Invalid query parameters")

    # gender validation
    if "gender" in params and params["gender"] not in allowed_gender:
        raise ValueError("Invalid query parameters")

    # age_group validation
    if "age_group" in params and params["age_group"] not in allowed_age_group:
        raise ValueError("Invalid query parameters")

    # min/max age type safety
    if "min_age" in params:
        try:
            int(params["min_age"])
        except:
            raise ValueError("Invalid query parameters")

    if "max_age" in params:
        try:
            int(params["max_age"])
        except:
            raise ValueError("Invalid query parameters")