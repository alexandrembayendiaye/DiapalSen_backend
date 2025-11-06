from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Categorie
from .serializers import CategorieSerializer, CategorieListSerializer


class CategorieListView(generics.ListAPIView):
    """
    API pour lister toutes les catégories actives
    Accessible à tous (pas d'authentification requise)
    """

    serializer_class = CategorieListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["est_active"]

    def get_queryset(self):
        return Categorie.objects.filter(est_active=True).order_by("ordre_affichage")


class CategorieDetailView(generics.RetrieveAPIView):
    """
    API pour récupérer les détails d'une catégorie
    """

    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Categorie.objects.filter(est_active=True)


@api_view(["GET"])
@permission_classes([AllowAny])
def categories_stats_view(request):
    """
    API pour les statistiques des catégories
    """
    categories = Categorie.objects.filter(est_active=True)

    stats = {
        "total_categories": categories.count(),
        "categories": CategorieListSerializer(categories, many=True).data,
    }

    return Response(stats, status=status.HTTP_200_OK)


# Pour les admins (plus tard)
class CategorieAdminListView(generics.ListCreateAPIView):
    """
    API admin pour gérer toutes les catégories (actives et inactives)
    Nécessite des permissions admin
    """

    serializer_class = CategorieSerializer
    # permission_classes = [IsAdminUser]  # À décommenter plus tard
    permission_classes = [AllowAny]  # Pour les tests

    def get_queryset(self):
        return Categorie.objects.all().order_by("ordre_affichage")


class CategorieAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API admin pour modifier/supprimer une catégorie
    """

    serializer_class = CategorieSerializer
    # permission_classes = [IsAdminUser]  # À décommenter plus tard
    permission_classes = [AllowAny]  # Pour les tests
    queryset = Categorie.objects.all()


from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Projet
from .serializers import (
    ProjetCreateSerializer,
    ProjetListSerializer,
    ProjetDetailSerializer,
    ProjetUpdateSerializer,
)


class ProjetCreateView(generics.CreateAPIView):
    """
    API pour créer un nouveau projet (brouillon)
    Accessible aux utilisateurs authentifiés (porteurs)
    """

    serializer_class = ProjetCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Vérifier que l'utilisateur peut créer des projets
        if self.request.user.type_utilisateur not in ["porteur", "admin"]:  # type: ignore
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Seuls les porteurs de projet peuvent créer des projets."
            )

        serializer.save(porteur=self.request.user)


class ProjetListView(generics.ListAPIView):
    """
    API pour lister les projets actifs (vue publique)
    """

    serializer_class = ProjetListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["categorie", "region", "statut"]

    def get_queryset(self):
        # Seulement les projets actifs pour le public
        return Projet.objects.filter(statut="actif").order_by("-date_creation")


class ProjetDetailView(generics.RetrieveAPIView):
    """
    API pour le détail d'un projet
    Accessible à tous + incrémente le nombre de vues
    """

    serializer_class = ProjetDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Projet.objects.filter(statut="actif")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémenter le nombre de vues
        instance.nombre_vues += 1
        instance.save(update_fields=["nombre_vues"])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MesProjetsListView(generics.ListAPIView):
    """
    API pour lister MES projets (porteur connecté)
    """

    serializer_class = ProjetListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Projet.objects.filter(porteur=self.request.user).order_by(
            "-date_creation"
        )


class ProjetUpdateView(generics.RetrieveUpdateAPIView):
    """
    API pour modifier un projet (seulement le porteur)
    """

    serializer_class = ProjetUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Projet.objects.filter(porteur=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def soumettre_projet_view(request, pk):
    """
    API pour soumettre un projet pour validation admin
    """
    try:
        projet = Projet.objects.get(pk=pk, porteur=request.user)
    except Projet.DoesNotExist:
        return Response(
            {"error": "Projet non trouvé"}, status=status.HTTP_404_NOT_FOUND
        )

    # Vérifications avant soumission
    if projet.statut != "brouillon":
        return Response(
            {"error": "Seuls les projets en brouillon peuvent être soumis"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not projet.image_principale:
        return Response(
            {"error": "Une image principale est requise"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Soumission
    projet.statut = "en_attente"
    projet.date_soumission = timezone.now()
    projet.save()

    # TODO: Notification à l'admin

    return Response(
        {
            "message": "Projet soumis avec succès pour validation !",
            "projet": ProjetDetailSerializer(projet).data,
        },
        status=status.HTTP_200_OK,
    )


# Vues admin (pour plus tard)
class ProjetAdminListView(generics.ListAPIView):
    """
    API admin pour lister tous les projets en attente
    """

    serializer_class = ProjetDetailSerializer
    permission_classes = [AllowAny]  # À changer plus tard en IsAdminUser

    def get_queryset(self):
        return Projet.objects.filter(statut="en_attente").order_by("date_soumission")


from .models import ValidationProjet
from .serializers import ValidationProjetSerializer, ProjetValidationSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # TODO: Changer en IsAdminUser plus tard
def valider_projet_view(request, pk):
    """
    API pour qu'un admin valide/rejette un projet
    """

    # Vérification admin (temporaire - à améliorer)
    if not request.user.is_superuser:
        return Response(
            {"error": "Seuls les administrateurs peuvent valider les projets"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        projet = Projet.objects.get(pk=pk, statut="en_attente")
    except Projet.DoesNotExist:
        return Response(
            {"error": "Projet non trouvé ou pas en attente de validation"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProjetValidationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    decision = serializer.validated_data["decision"]  # type: ignore
    commentaire = serializer.validated_data["commentaire"]  # type: ignore

    # Traitement selon la décision
    if decision == "approuve":
        type_financement = serializer.validated_data["type_financement"]  # type: ignore

        # Mise à jour du projet
        projet.statut = "actif"
        projet.type_financement = type_financement
        projet.commentaire_admin_financement = commentaire
        projet.date_validation = timezone.now()
        projet.date_debut_campagne = timezone.now()
        projet.date_fin_campagne = timezone.now() + timedelta(
            days=projet.duree_campagne_jours
        )
        projet.save()

        # Enregistrement de la validation
        validation = ValidationProjet.objects.create(
            projet=projet,
            administrateur=request.user,
            decision=decision,
            type_financement_choisi=type_financement,
            commentaire=commentaire,
        )

        message = f"Projet approuvé avec le type de financement '{projet.get_type_financement_display()}'"  # type: ignore

    elif decision == "rejete":
        motif_rejet = serializer.validated_data["motif_rejet"]  # type: ignore

        # Mise à jour du projet
        projet.statut = "rejete"
        projet.motif_rejet = motif_rejet
        projet.date_validation = timezone.now()
        projet.save()

        # Enregistrement de la validation
        validation = ValidationProjet.objects.create(
            projet=projet,
            administrateur=request.user,
            decision=decision,
            commentaire=commentaire,
            motif_rejet=motif_rejet,
        )

        message = "Projet rejeté"

    # TODO: Envoyer email au porteur

    return Response(
        {
            "message": message,
            "projet": ProjetDetailSerializer(projet).data,
            "validation": ValidationProjetSerializer(validation).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # TODO: IsAdminUser
def historique_validations_view(request):
    """
    API pour voir l'historique des validations
    """
    if not request.user.is_superuser:
        return Response(
            {"error": "Accès admin requis"}, status=status.HTTP_403_FORBIDDEN
        )

    validations = ValidationProjet.objects.all().order_by("-date_validation")
    serializer = ValidationProjetSerializer(validations, many=True)

    return Response({"validations": serializer.data, "total": validations.count()})
