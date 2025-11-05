from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import InscriptionSerializer, UtilisateurSerializer

Utilisateur = get_user_model()


# ============================================================
# 1️⃣ Inscription (POST /api/users/register/)
# ============================================================
class InscriptionView(generics.CreateAPIView):
    """
    Vue permettant à un nouvel utilisateur de s'inscrire.
    """

    serializer_class = InscriptionSerializer
    permission_classes = [permissions.AllowAny]  # tout le monde peut s'inscrire


# ============================================================
# 2️⃣ Profil utilisateur connecté (GET / PUT /api/users/me/)
# ============================================================
class ProfilView(APIView):
    """
    Vue pour récupérer ou mettre à jour le profil de l'utilisateur connecté.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retourne les informations du profil courant."""
        serializer = UtilisateurSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Met à jour les informations du profil courant."""
        serializer = UtilisateurSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
