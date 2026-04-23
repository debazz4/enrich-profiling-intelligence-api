def apply_sorting(queryset, params):
    sort_by = params.get("sort_by")
    order = params.get("order", "asc")

    allowed_fields = ["age", "created_at", "gender_probability"]
    allowed_orders = ["asc", "desc"]

    # Validate sort_by
    if sort_by:
        if sort_by not in allowed_fields:
            raise ValueError("Invalid query parameters")

    # Validate order
    if order not in allowed_orders:
        raise ValueError("Invalid query parameters")

    # Apply sorting
    if sort_by:
        if order == "desc":
            sort_by = f"-{sort_by}"
        queryset = queryset.order_by(sort_by)

    return queryset