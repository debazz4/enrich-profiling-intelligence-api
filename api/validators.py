from rest_framework.response import Response
from rest_framework import status


def validate_query_params(params):
    errors = {}

    # min_age validation
    min_age = params.get("min_age")
    try:
        max_age = int(min_age)
    except (TypeError, ValueError):
        return Response(
            {
                "status": "error",
                "message": "Invalid query parameters"
            },
            status=422
    )
    # max_age validation
    max_age = params.get("max_age")
    try:
        max_age = int(max_age)
    except (TypeError, ValueError):
        return Response(
            {
                "status": "error",
                "message": "Invalid query parameters"
            },
            status=422
    )
        
    # min_gender_probability
    mgp = params.get("min_gender_probability")
    if mgp is not None:
        try:
            float(mgp)
        except ValueError:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid query parameters"
                },
                status=422
            )

    # min_country_probability
    mcp = params.get("min_country_probability")
    if mcp is not None:
        try:
            float(mcp)
        except ValueError:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid query parameters"
                },
                status=422
            )

    return None