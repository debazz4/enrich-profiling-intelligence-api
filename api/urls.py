from django.urls import path
from dj_rest_auth.jwt_auth import get_refresh_view
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    ProfileListCreateView, 
    ProfileDetailView, 
    ProfileSearchView,
    GitHubCallbackView,
    GitHubLoginView,
    ExportProfilesView,
    LogoutView,
    GitHubLoginCLIView,
    # GitHubCallbackCLIView
)
# from .auth.views import CSRFTokenView

urlpatterns = [
    path("profiles", ProfileListCreateView.as_view()),
    path("profiles/<uuid:id>", ProfileDetailView.as_view()),
    path("profiles/search", ProfileSearchView.as_view()),
    path("profiles/export", ExportProfilesView.as_view()),
    path("auth/github/cli/login/", GitHubLoginCLIView.as_view()),
    # path("auth/github/cli/callback/", GitHubCallbackCLIView.as_view()),
    path("auth/github/login/", GitHubLoginView.as_view()),
    path("auth/github/callback/", GitHubCallbackView.as_view()),

    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", get_refresh_view().as_view()),
    path("auth/logout", LogoutView.as_view()),

    # To import CSRFToken
    # path("auth/csrf", CSRFTokenView.as_view()),
]