def apply_pagination(queryset, params):
    try:
        page = int(params.get("page", 1))
        limit = int(params.get("limit", 10))

        if page < 1:
            raise ValueError

        limit = min(limit, 50)  # enforce max

        start = (page - 1) * limit
        end = start + limit

        total = queryset.count()
        data = queryset[start:end]

        return data, total, page, limit

    except ValueError:
        raise ValueError("Invalid query parameters")