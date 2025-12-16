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
            
            # Vérifier si c'est la première contribution de cet utilisateur
            from .models import Contribution as ContributionModel
            nb_contributions_existantes = ContributionModel.objects.filter(
                projet=projet,
                contributeur=contribution.contributeur,
                statut_paiement="valide"
            ).exclude(id=contribution.id).count()
            
            # N'incrémenter que si c'est un nouveau contributeur
            if nb_contributions_existantes == 0:
                projet.nombre_contributeurs += 1
                projet.save(update_fields=["montant_collecte", "nombre_contributeurs"])
            else:
                projet.save(update_fields=["montant_collecte"])

            recu_pdf = generer_recu_pdf(contribution)
            contribution.recu_pdf.save(  # type: ignore
                f"recu_{contribution.reference_paiement}.pdf",  # type: ignore
                recu_pdf,
                save=False,
            )

        contribution.save()  # type: ignore

        # Créer les notifications si le paiement est validé
        if resultat_paiement["succes"]:
            from apps.notifications.models import Notification
            
            # Notification pour le contributeur
            Notification.objects.create(
                destinataire=contribution.contributeur,
                type_notification="contribution_confirmee",
                titre="Contribution confirmée !",
                contenu=f"Votre contribution de {int(contribution.montant):,} FCFA au projet '{projet.titre}' a été validée.".replace(",", " "),
                lien_action=f"/projets/{projet.id}",
                donnees_contextuelles={
                    "contribution_id": contribution.id,
                    "montant": str(contribution.montant),
                    "projet_id": projet.id,
                },
            )
            
            # Notification pour le porteur de projet
            Notification.objects.create(
                destinataire=projet.porteur,
                type_notification="nouvelle_contribution",
                titre="Nouvelle contribution reçue !",
                contenu=f"{contribution.contributeur_nom_affiche} a contribué {int(contribution.montant):,} FCFA à votre projet '{projet.titre}'.".replace(",", " "),
                lien_action=f"/mes-projets/{projet.id}/stats",
                donnees_contextuelles={
                    "contribution_id": contribution.id,
                    "montant": str(contribution.montant),
                    "contributeur": contribution.contributeur_nom_affiche,
                },
            )

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mes_contributeurs_view(request):
    """
    API pour récupérer tous les contributeurs de tous les projets du porteur connecté
    """
    # Récupérer tous les projets du porteur
    mes_projets = Projet.objects.filter(porteur=request.user)
    
    # Récupérer toutes les contributions validées pour ces projets
    contributions = Contribution.objects.filter(
        projet__in=mes_projets,
        statut_paiement="valide"
    ).select_related('contributeur', 'projet').order_by("-date_contribution")
    
    # Grouper par contributeur
    contributeurs_dict = {}
    for contrib in contributions:
        contributeur_id = contrib.contributeur.id
        if contributeur_id not in contributeurs_dict:
            contributeurs_dict[contributeur_id] = {
                "id": contributeur_id,
                "nom_complet": contrib.contributeur.get_full_name() or "Anonyme",
                "email": contrib.contributeur.email,
                "contributions": [],
                "total_contribution": 0,
                "nombre_contributions": 0,
                "projets_soutenus": set()
            }
        
        contributeurs_dict[contributeur_id]["contributions"].append({
            "id": contrib.id,
            "projet_id": contrib.projet.id,
            "projet_titre": contrib.projet.titre,
            "montant": float(contrib.montant),
            "date_contribution": contrib.date_contribution,
            "message_soutien": contrib.message_soutien
        })
        contributeurs_dict[contributeur_id]["total_contribution"] += float(contrib.montant)
        contributeurs_dict[contributeur_id]["nombre_contributions"] += 1
        contributeurs_dict[contributeur_id]["projets_soutenus"].add(contrib.projet.titre)
    
    # Convertir en liste et formater
    contributeurs_list = []
    for contrib_data in contributeurs_dict.values():
        contrib_data["projets_soutenus"] = list(contrib_data["projets_soutenus"])
        contributeurs_list.append(contrib_data)
    
    # Trier par montant total décroissant
    contributeurs_list.sort(key=lambda x: x["total_contribution"], reverse=True)
    
    # Stats globales
    stats = {
        "total_contributeurs": len(contributeurs_list),
        "total_contributions": sum(c["nombre_contributions"] for c in contributeurs_list),
        "montant_total": sum(c["total_contribution"] for c in contributeurs_list),
        "montant_moyen": sum(c["total_contribution"] for c in contributeurs_list) / len(contributeurs_list) if contributeurs_list else 0
    }
    
    return Response({
        "contributeurs": contributeurs_list,
        "stats": stats
    })

