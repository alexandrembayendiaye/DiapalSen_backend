from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Contribution
from apps.projects.models import Projet
from .serializers import (
    ContributionCreateSerializer,
    ContributionListSerializer,
    ContributionDetailSerializer,
    MesContributionsSerializer,
)
from .utils import simuler_paiement, generer_recu_pdf


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def contribuer_projet_view(request, projet_id):
    """
    API pour contribuer à un projet
    """
    projet = get_object_or_404(Projet, id=projet_id, statut="actif")

    # Vérifier que l'utilisateur n'est pas le porteur du projet
    if projet.porteur == request.user:
        return Response(
            {"error": "Vous ne pouvez pas contribuer à votre propre projet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Créer la contribution
    serializer = ContributionCreateSerializer(
        data=request.data, context={"request": request}
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        # Sauvegarder la contribution
        contribution = serializer.save(projet=projet)

        # Simuler le paiement
        resultat_paiement = simuler_paiement(
            contribution.moyen_paiement,  # type: ignore
            contribution.montant,  # type: ignore
            contribution.reference_paiement,  # type: ignore
        )

        # Mettre à jour la contribution avec le résultat
        contribution.statut_paiement = resultat_paiement["statut"]  # type: ignore
        contribution.donnees_paiement = resultat_paiement["donnees"]  # type: ignore

        if resultat_paiement["succes"]:
            # Mise à jour du projet
            projet.montant_collecte += contribution.montant  # type: ignore
            projet.nombre_contributeurs += 1
            projet.save(update_fields=["montant_collecte", "nombre_contributeurs"])

            # Générer le reçu PDF
            recu_pdf = generer_recu_pdf(contribution)
            contribution.recu_pdf.save(  # type: ignore
                f"recu_{contribution.reference_paiement}.pdf",  # type: ignore
                recu_pdf,
                save=False,
            )

        contribution.save()  # type: ignore

        # TODO: Envoyer notifications email

        return Response(
            {
                "message": resultat_paiement["message"],
                "contribution": ContributionDetailSerializer(contribution).data,
                "projet_mis_a_jour": {
                    "montant_collecte": float(projet.montant_collecte),
                    "pourcentage_atteint": projet.pourcentage_atteint,
                    "nombre_contributeurs": projet.nombre_contributeurs,
                },
            },
            status=(
                status.HTTP_201_CREATED
                if resultat_paiement["succes"]
                else status.HTTP_400_BAD_REQUEST
            ),
        )


class ContributionsProjetListView(generics.ListAPIView):
    """
    API pour lister les contributions d'un projet (vue publique)
    """

    serializer_class = ContributionListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        projet_id = self.kwargs["projet_id"]
        return Contribution.objects.filter(
            projet_id=projet_id, statut_paiement="valide"
        ).order_by("-date_contribution")


class MesContributionsListView(generics.ListAPIView):
    """
    API pour lister les contributions de l'utilisateur connecté
    """

    serializer_class = MesContributionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contribution.objects.filter(contributeur=self.request.user).order_by(
            "-date_contribution"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ma_contribution_detail_view(request, contribution_id):
    """
    API pour voir le détail d'une de mes contributions
    """
    contribution = get_object_or_404(
        Contribution, id=contribution_id, contributeur=request.user
    )

    serializer = ContributionDetailSerializer(contribution)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def statistiques_contributions_view(request):
    """
    API pour les statistiques de contributions de l'utilisateur
    """
    contributions = Contribution.objects.filter(
        contributeur=request.user, statut_paiement="valide"
    )

    stats = {
        "nombre_contributions": contributions.count(),
        "montant_total_contribue": sum(c.montant for c in contributions),
        "nombre_projets_soutenus": contributions.values("projet").distinct().count(),
        "derniere_contribution": None,
    }

    derniere = contributions.first()
    if derniere:
        stats["derniere_contribution"] = {
            "projet_titre": derniere.projet.titre,
            "montant": float(derniere.montant),
            "date": derniere.date_contribution,
        }

    return Response(stats)
