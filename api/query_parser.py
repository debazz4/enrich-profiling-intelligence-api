def validate_filters(filters):
    if "min_age" in filters and "max_age" in filters:
        if filters["min_age"] > filters["max_age"]:
            raise ValueError("Invalid age range")