from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Projet, MiseAJourProjet
from .serializers_updates import (
    MiseAJourProjetCreateSerializer,
    MiseAJourProjetSerializer,
)
from django.db import models


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def publier_mise_a_jour_view(request, projet_id):
    """
    API pour publier une mise à jour sur un projet (porteur uniquement)
    """
    projet = get_object_or_404(Projet, id=projet_id, porteur=request.user)

    if projet.statut not in ["actif", "finance"]:
        return Response(
            {
                "error": "Vous ne pouvez publier des mises à jour que sur des projets actifs ou financés."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = MiseAJourProjetCreateSerializer(
        data=request.data, context={"request": request, "projet": projet}
    )

    if serializer.is_valid():
        mise_a_jour = serializer.save()

        # TODO: Notifier les contributeurs

        return Response(
            {
                "message": "Mise à jour publiée avec succès !",
                "mise_a_jour": MiseAJourProjetSerializer(mise_a_jour).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MisesAJourProjetListView(generics.ListAPIView):
    """
    API pour lister les mises à jour d'un projet
    """

    serializer_class = MiseAJourProjetSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        projet_id = self.kwargs["projet_id"]
        queryset = MiseAJourProjet.objects.filter(projet_id=projet_id)

        # Filtrer selon la visibilité et l'utilisateur
        user = self.request.user
        if not user.is_authenticated:
            return queryset.filter(visibilite="public")

        # Utilisateur connecté : voir publiques + ses contributions
        return queryset.filter(
            models.Q(visibilite="public")
            | (
                models.Q(visibilite="contributeurs")
                & models.Q(
                    projet__contributions__contributeur=user,
                    projet__contributions__statut_paiement="valide",
                )
            )
        ).distinct()
