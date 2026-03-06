from django.urls import path
<<<<<<< HEAD
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import InscriptionView, ProfilView

urlpatterns = [
    # Inscription
    path("register/", InscriptionView.as_view(), name="register"),
    # Connexion / rafraîchissement JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profil utilisateur connecté
    path("me/", ProfilView.as_view(), name="me"),
]
=======
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

>>>>>>> ancienne_version
