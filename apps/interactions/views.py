from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Commentaire, Favori, Partage
from apps.projects.models import Projet
from .serializers import (
    CommentaireCreateSerializer,
    CommentaireSerializer,
    FavoriSerializer,
    PartageCreateSerializer,
)


class CommentairesProjetListView(generics.ListAPIView):
    """
    API pour lister les commentaires d'un projet
    """

    serializer_class = CommentaireSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        projet_id = self.kwargs["projet_id"]
        # Seulement les commentaires principaux (pas les réponses)
        return Commentaire.objects.filter(
            projet_id=projet_id, commentaire_parent=None, est_masque=False
        ).order_by("-date_creation")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ajouter_commentaire_view(request, projet_id):
    """
    API pour ajouter un commentaire à un projet
    """
    projet = get_object_or_404(Projet, id=projet_id, statut="actif")

    serializer = CommentaireCreateSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        commentaire = serializer.save(projet=projet)

        # TODO: Notification au porteur de projet

        return Response(
            {
                "message": "Commentaire ajouté avec succès !",
                "commentaire": CommentaireSerializer(
                    commentaire, context={"request": request}
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def favori_toggle_view(request, projet_id):
    """
    API pour ajouter/retirer un projet des favoris
    """
    projet = get_object_or_404(Projet, id=projet_id)

    if request.method == "POST":
        try:
            favori, created = Favori.objects.get_or_create(
                utilisateur=request.user, projet=projet
            )
            if created:
                return Response(
                    {"message": "Projet ajouté aux favoris !", "favori": True}
                )
            else:
                return Response(
                    {"message": "Projet déjà dans vos favoris", "favori": True}
                )
        except IntegrityError:
            return Response({"message": "Projet déjà dans vos favoris", "favori": True})

    elif request.method == "DELETE":
        deleted, _ = Favori.objects.filter(
            utilisateur=request.user, projet=projet
        ).delete()

        if deleted:
            return Response({"message": "Projet retiré des favoris", "favori": False})
        else:
            return Response({"message": "Projet pas dans vos favoris", "favori": False})


class MesFavorisListView(generics.ListAPIView):
    """
    API pour lister mes projets favoris
    """

    serializer_class = FavoriSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favori.objects.filter(utilisateur=self.request.user)


@api_view(["POST"])
@permission_classes([AllowAny])
def partager_projet_view(request, projet_id):
    """
    API pour enregistrer un partage de projet
    """
    projet = get_object_or_404(Projet, id=projet_id)

    serializer = PartageCreateSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        partage = serializer.save(projet=projet)

        # Incrémenter le nombre de partages du projet
        projet.nombre_partages += 1
        projet.save(update_fields=["nombre_partages"])

        return Response(
            {
                "message": "Partage enregistré !",
                "nouveau_total": projet.nombre_partages,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .models import Signalement
from .serializers import SignalementCreateSerializer, SignalementListSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def signaler_contenu_view(request):
    """
    API pour signaler un contenu inapproprié
    """
    serializer = SignalementCreateSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        try:
            signalement = serializer.save()
            return Response(
                {
                    "message": "Signalement envoyé avec succès. Nous examinerons votre rapport.",
                    "signalement_id": signalement.id,  # type: ignore
                },
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"error": "Vous avez déjà signalé cet élément."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vue admin pour les signalements
class SignalementsAdminListView(generics.ListAPIView):
    """API admin pour lister tous les signalements"""

    serializer_class = SignalementListSerializer
    permission_classes = [AllowAny]  # TODO: IsAdminUser

    def get_queryset(self):
        return Signalement.objects.all().order_by("-date_signalement")
