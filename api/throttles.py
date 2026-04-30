from rest_framework.throttling import UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    scope = "burst"


class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"


class SearchRateThrottle(UserRateThrottle):
    scope = "search"


class ExportRateThrottle(UserRateThrottle):
    scope = "export"