from django.urls import path
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
]
