from django.urls import path
from .views import (
    CategorieListView,
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    MyProjectsView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectStatusUpdateView,
)

urlpatterns = [
    path("", ProjectListView.as_view(), name="project-list"),
    path("create/", ProjectCreateView.as_view(), name="project-create"),
    path("<uuid:id>/", ProjectDetailView.as_view(), name="project-detail"),
    path("mine/", MyProjectsView.as_view(), name="my-projects"),
    path("<uuid:pk>/update/", ProjectUpdateView.as_view(), name="project-update"),
    path("<uuid:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
    path("categories/", CategorieListView.as_view(), name="categorie-list"),
    path(
        "<uuid:pk>/update_status/",
        ProjectStatusUpdateView.as_view(),
        name="update_status",
    ),
]
