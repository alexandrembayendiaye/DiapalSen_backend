from django.urls import path
from .views import (
    ContributionCreateView,
    ProjectContributionsListView,
    UserContributionsListView,
    ContributionConfirmView,
    ContributionDetailView,
)

urlpatterns = [
    path("create/", ContributionCreateView.as_view(), name="create_contribution"),
    path(
        "project/<uuid:projet_id>/",
        ProjectContributionsListView.as_view(),
        name="project_contributions",
    ),
    path("my/", UserContributionsListView.as_view(), name="my_contributions"),
    path(
        "<uuid:pk>/confirmer/",
        ContributionConfirmView.as_view(),
        name="confirmer_contribution",
    ),
    path(
        "<uuid:pk>/", ContributionDetailView.as_view(), name="detail_contribution"
    ),  # 👈 ajout ici
]
