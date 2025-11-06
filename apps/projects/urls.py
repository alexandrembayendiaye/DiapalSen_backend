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
]
