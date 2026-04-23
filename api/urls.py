from django.urls import path
from .views import ProfileListCreateView, ProfileDetailView, ProfileSearchView

urlpatterns = [
    path("profiles", ProfileListCreateView.as_view()),
    path("profiles/<uuid:id>", ProfileDetailView.as_view()),
    path("profiles/search", ProfileSearchView.as_view()),
]