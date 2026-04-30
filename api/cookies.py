from django.conf import settings

def set_auth_cookies(response, access_token, refresh_token=None):
    """
    Attach JWT tokens as HTTP-only cookies for web portal authentication.
    """

    # Access token (short-lived)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,   # set True in production (HTTPS)
        samesite="Lax",
        max_age=60 * 15  # 15 minutes
    )

    # Refresh token (long-lived)
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7  # 7 days
        )

    return response