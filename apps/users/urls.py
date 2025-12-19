from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="user-register"),
    path("login/", views.login_view, name="user-login"),
    path("logout/", views.logout_view, name="user-logout"),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("dashboard/", views.user_dashboard_view, name="user-dashboard"),
    path("stats/", views.user_stats_view, name="user-stats"),
    path("change-profile-type/", views.change_profile_type_view, name="change-profile-type"),
]

