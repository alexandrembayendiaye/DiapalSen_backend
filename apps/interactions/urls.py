from django.urls import path
from . import views

urlpatterns = [
    # Commentaires
    path(
        "projet/<int:projet_id>/commentaires/",
        views.CommentairesProjetListView.as_view(),
        name="commentaires-projet",
    ),
    path(
        "projet/<int:projet_id>/commenter/",
        views.ajouter_commentaire_view,
        name="ajouter-commentaire",
    ),
    # Favoris
    path(
        "projet/<int:projet_id>/favori/", views.favori_toggle_view, name="favori-toggle"
    ),
    path("mes-favoris/", views.MesFavorisListView.as_view(), name="mes-favoris"),
    # Partages
    path(
        "projet/<int:projet_id>/partager/",
        views.partager_projet_view,
        name="partager-projet",
    ),
    # Signalements (ajoutez cette ligne)
    path("signaler/", views.signaler_contenu_view, name="signaler-contenu"),
    path(
        "admin/signalements/",
        views.SignalementsAdminListView.as_view(),
        name="admin-signalements",
    ),
]
