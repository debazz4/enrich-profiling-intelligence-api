def apply_filters(queryset, params):
    try:
        gender = params.get("gender")
        age_group = params.get("age_group")
        country_id = params.get("country_id")

        min_age = params.get("min_age")
        max_age = params.get("max_age")

        min_gender_prob = params.get("min_gender_probability")
        min_country_prob = params.get("min_country_probability")

        if gender:
            queryset = queryset.filter(gender__iexact=gender)

        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)

        if country_id:
            queryset = queryset.filter(country_id__iexact=country_id)

        if min_age:
            queryset = queryset.filter(age__gte=int(min_age))

        if max_age:
            queryset = queryset.filter(age__lte=int(max_age))

        if min_gender_prob:
            queryset = queryset.filter(
                gender_probability__gte=float(min_gender_prob)
            )

        if min_country_prob:
            queryset = queryset.filter(
                country_probability__gte=float(min_country_prob)
            )

        if country_id:
            queryset = queryset.filter(country_id__gte=country_id)

        return queryset

    except ValueError:
        raise ValueError("Invalid query parameters")