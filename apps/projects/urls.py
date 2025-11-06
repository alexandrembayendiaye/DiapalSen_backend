from django.urls import path
from . import views

urlpatterns = [
    # APIs publiques
    path("categories/", views.CategorieListView.as_view(), name="categories-list"),
    path(
        "categories/<int:pk>/",
        views.CategorieDetailView.as_view(),
        name="categories-detail",
    ),
    path("categories/stats/", views.categories_stats_view, name="categories-stats"),
    # APIs admin
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
    path("edit/<int:pk>/", views.ProjetUpdateView.as_view(), name="projets-edit"),
    path("<int:pk>/soumettre/", views.soumettre_projet_view, name="projets-soumettre"),
    # APIs admin projets
    path(
        "admin/en-attente/",
        views.ProjetAdminListView.as_view(),
        name="admin-projets-attente",
    ),
]
