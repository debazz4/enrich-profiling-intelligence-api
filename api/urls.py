from django.urls import path
from .views import ProfileListCreateView, ProfileDetailView

urlpatterns = [
    path("profiles", ProfileListCreateView.as_view()),
    path("profiles/<uuid:id>", ProfileDetailView.as_view()),
]