from django.urls import path
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
