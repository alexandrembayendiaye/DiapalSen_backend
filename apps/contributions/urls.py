from django.urls import path
<<<<<<< HEAD
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
=======
from . import views

urlpatterns = [
    # Contributions
    path(
        "projet/<int:projet_id>/contribuer/",
        views.contribuer_projet_view,
        name="contribuer-projet",
    ),
    path(
        "projet/<int:projet_id>/contributions/",
        views.ContributionsProjetListView.as_view(),
        name="contributions-projet",
    ),
    # Mes contributions
    path(
        "mes-contributions/",
        views.MesContributionsListView.as_view(),
        name="mes-contributions",
    ),
    path(
        "mes-contributions/<int:contribution_id>/",
        views.ma_contribution_detail_view,
        name="ma-contribution-detail",
    ),
    path(
        "mes-contributions/stats/",
        views.statistiques_contributions_view,
        name="stats-contributions",
    ),
    # Contributeurs du porteur
    path(
        "mes-contributeurs/",
        views.mes_contributeurs_view,
        name="mes-contributeurs",
    ),
>>>>>>> ancienne_version
]
