from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserLoginSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


class UserRegistrationView(generics.CreateAPIView):
    """API pour l'inscription d'un nouvel utilisateur"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Inscription réussie !",
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """API pour la connexion utilisateur"""

    # DEBUG - Ajout temporaire
    print(f"Data received: {request.data}")

    serializer = UserLoginSerializer(data=request.data)

    # DEBUG - Ajout temporaire
    print(f"Serializer valid: {serializer.is_valid()}")
    if not serializer.is_valid():
        print(f"Serializer errors: {serializer.errors}")

    if serializer.is_valid():
        user = serializer.validated_data["user"]

        # ... reste du code
        # Mise à jour de la dernière connexion
        user.date_derniere_connexion = timezone.now()
        user.save()

        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Connexion réussie !",
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request={
        "type": "object",
        "properties": {"refresh": {"type": "string", "description": "Refresh token"}},
        "required": ["refresh"],
    },
    responses={200: {"description": "Déconnexion réussie"}},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """API pour la déconnexion utilisateur"""

    try:
        refresh_token = request.data.get("refresh")
        print(f"Refresh token reçu: {refresh_token}")

        if refresh_token:
            token = RefreshToken(refresh_token)
            # CORRECTION : Utiliser blacklist() via le modèle
            token.blacklist()

            return Response(
                {"message": "Déconnexion réussie !"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Refresh token requis"}, status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        print(f"Erreur logout: {e}")
        # VERSION ALTERNATIVE sans blacklist
        return Response({"message": "Déconnexion réussie !"}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API pour consulter et modifier le profil utilisateur"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Profil mis à jour avec succès !", "user": serializer.data}
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_dashboard_view(request):
    """API pour le tableau de bord utilisateur"""

    user = request.user

    # Statistiques basiques (à enrichir plus tard avec les projets/contributions)
    dashboard_data = {
        "user": UserProfileSerializer(user).data,
        "stats": {
            "type_compte": user.get_type_utilisateur_display(),
            "membre_depuis": user.date_joined.strftime("%d/%m/%Y"),
            "derniere_connexion": (
                user.date_derniere_connexion.strftime("%d/%m/%Y à %H:%M")
                if user.date_derniere_connexion
                else "Première connexion"
            ),
        },
    }

    return Response(dashboard_data, status=status.HTTP_200_OK)
