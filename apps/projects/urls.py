from django.urls import path
from . import views
from . import views_updates

urlpatterns = [
    # APIs publiques
    path("categories/", views.CategorieListView.as_view(), name="categories-list"),
    path(
        "categories/<int:pk>/",
        views.CategorieDetailView.as_view(),
        name="categories-detail",
    ),
    path("categories/stats/", views.categories_stats_view, name="categories-stats"),
    # APIs admin catégories
    path(
        "admin/categories/",
        views.CategorieAdminListView.as_view(),
        name="admin-categories-list",
    ),
    path(
        "admin/categories/<int:pk>/",
        views.CategorieAdminDetailView.as_view(),
        name="admin-categories-detail",
    ),
    # APIs projets publiques
    path("", views.ProjetListView.as_view(), name="projets-list"),
    path("<int:pk>/", views.ProjetDetailView.as_view(), name="projets-detail"),
    # APIs projets porteur
    path("create/", views.ProjetCreateView.as_view(), name="projets-create"),
    path("mes-projets/", views.MesProjetsListView.as_view(), name="mes-projets"),
    path(
        "mes-projets/<int:pk>/",
        views.MonProjetDetailView.as_view(),
        name="mon-projet-detail",
    ),
    path("edit/<int:pk>/", views.ProjetUpdateView.as_view(), name="projets-edit"),
    path("<int:pk>/soumettre/", views.soumettre_projet_view, name="projets-soumettre"),
    path("<int:pk>/upload-image/", views.upload_image_view, name="upload-image"),
    # APIs admin projets
    path(
        "admin/en-attente/",
        views.ProjetAdminListView.as_view(),
        name="admin-projets-attente",
    ),
    path(
        "admin/valider/<int:pk>/",
        views.valider_projet_view,
        name="admin-valider-projet",
    ),
    path(
        "admin/validations/",
        views.historique_validations_view,
        name="admin-historique-validations",
    ),
    path("admin/stats/", views.admin_stats_view, name="admin-stats"),
    path("admin/users/", views.admin_users_list_view, name="admin-users"),
    # Mises à jour projets
    path(
        "<int:projet_id>/mise-a-jour/publier/",
        views_updates.publier_mise_a_jour_view,
        name="publier-mise-a-jour",
    ),
    path(
        "<int:projet_id>/mises-a-jour/",
        views_updates.MisesAJourProjetListView.as_view(),
        name="mises-a-jour-projet",
    ),
]
