def apply_sorting(queryset, params):

    sort_by = params.get("sort_by")
    order = params.get("order", "asc")

    allowed_fields = {
        "age": "age",
        "created_at": "created_at",
        "gender_probability": "gender_probability"
    }

    if sort_by not in allowed_fields:
        return queryset

    field = allowed_fields[sort_by]

    if order == "desc":
        field = f"-{field}"

    return queryset.order_by(field)