<<<<<<< HEAD
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.exceptions import PermissionDenied
from .serializers import ProjectSerializer
from .models import Categorie
from .serializers import CategorieSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProjectStatusUpdateSerializer


class CategorieListView(generics.ListAPIView):
    """
    Liste publique des catégories actives
    """

    queryset = Categorie.objects.filter(est_active=True).order_by("ordre_affichage")
    serializer_class = CategorieSerializer
    permission_classes = [permissions.AllowAny]


class ProjectListView(generics.ListAPIView):
    """
    Liste publique des projets validés.
    Accessible à tous (même sans authentification).
    """

    queryset = Project.objects.filter(statut="actif").select_related(
        "categorie", "porteur"
    )
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["categorie__nom", "statut"]


class ProjectDetailView(generics.RetrieveAPIView):
    """
    Détail d'un projet spécifique.
    Accessible à tous.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"


class ProjectCreateView(generics.CreateAPIView):
    """
    Création d'un nouveau projet.
    Réservé aux utilisateurs connectés (porteurs).
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Associe automatiquement le projet à l'utilisateur connecté.
        """
        user = self.request.user
        serializer.save(porteur=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyProjectsView(generics.ListAPIView):
    """
    Liste des projets du porteur connecté.
    """

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(porteur=user).order_by("-date_creation")


class ProjectUpdateView(generics.UpdateAPIView):
    """
    Permet au porteur de modifier son projet tant qu'il n'est pas validé.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        project = self.get_object()

        # Vérifie si c’est bien le porteur du projet
        if project.porteur != self.request.user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres projets.")

        # Vérifie le statut
        if project.statut not in ["brouillon", "rejete"]:
            raise PermissionDenied(
                "Vous ne pouvez plus modifier un projet validé ou en cours."
            )

        serializer.save()


class ProjectDeleteView(generics.DestroyAPIView):
    """
    Permet au porteur de supprimer son projet tant qu'il n'est pas validé.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        # Vérifie si c’est bien le porteur du projet
        if instance.porteur != self.request.user:
            raise PermissionDenied("Vous ne pouvez supprimer que vos propres projets.")

        # Vérifie le statut
        if instance.statut not in ["brouillon", "rejete"]:
            raise PermissionDenied(
                "Vous ne pouvez pas supprimer un projet validé ou actif."
            )

        instance.delete()


class ProjectStatusUpdateView(generics.UpdateAPIView):
    """
    Vue pour mettre à jour le statut d’un projet.
    Accessible uniquement au porteur du projet ou à un admin.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        project = self.get_object()

        # 🔒 Vérifie les droits
        if request.user != project.porteur and not request.user.is_staff:
            return Response(
                {"detail": "Vous n’avez pas l’autorisation de modifier ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
=======
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
        # Les admins peuvent voir tous les projets
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return Projet.objects.all()
        # Les visiteurs ne voient que les projets actifs
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
    if projet.statut not in ["brouillon", "modification_demandee"]:
        return Response(
            {"error": "Seuls les projets en brouillon ou en modification demandée peuvent être soumis"},
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
    projet.motif_rejet = None  # Effacer le motif précédent
    projet.save()

    # Notification aux admins
    from apps.notifications.utils import notifier_projet_soumis_admin
    notifier_projet_soumis_admin(projet)

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

    elif decision == "infos_demandees":
        # Demande de modification
        projet.statut = "modification_demandee"
        projet.motif_rejet = commentaire  # On utilise le commentaire comme motif
        projet.date_validation = timezone.now()
        projet.save()

        # Enregistrement de la validation
        validation = ValidationProjet.objects.create(
            projet=projet,
            administrateur=request.user,
            decision=decision,
            commentaire=commentaire,
        )

        message = "Modifications demandées au porteur"

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


class MonProjetDetailView(generics.RetrieveAPIView):
    """
    API pour qu'un porteur accède aux détails de SES projets
    (peu importe le statut)
    """

    serializer_class = ProjetDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Le porteur peut voir tous SES projets
        return Projet.objects.filter(porteur=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Pas d'incrémentation de vues pour le porteur
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_image_view(request, pk):
    """
    API pour upload d'image principale d'un projet
    Accessible seulement au porteur du projet
    """
    try:
        # Récupérer le projet (seulement si c'est le porteur)
        projet = Projet.objects.get(pk=pk, porteur=request.user)

        # Bloquer l'upload pour les projets actifs ou en attente
        if projet.statut in ["actif", "en_attente"]:
            return Response(
                {"error": "L'image ne peut plus être modifiée pour un projet en attente de validation ou actif"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier qu'il y a une image dans la requête
        if "image_principale" not in request.FILES:
            return Response(
                {"error": "Aucune image fournie"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Sauvegarder l'image
        projet.image_principale = request.FILES["image_principale"]
        projet.save(update_fields=["image_principale"])

        return Response(
            {
                "message": "Image uploadée avec succès",
                "image_url": (
                    projet.image_principale.url if projet.image_principale else None
                ),
                "projet_id": projet.id,  # type: ignore
            },
            status=status.HTTP_200_OK,
        )

    except Projet.DoesNotExist:
        return Response(
            {"error": "Projet non trouvé ou vous n'êtes pas le porteur"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"Erreur lors de l'upload: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ✅ NOUVELLES VUES À AJOUTER dans votre fichier projets/views.py
# Ajoutez ces imports en haut du fichier si pas déjà présents :

from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()

# ✅ AJOUTEZ CETTE VUE À LA FIN DE votre fichier views.py :


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # TODO: Changer en IsAdminUser plus tard
def admin_stats_view(request):
    """
    API pour les statistiques globales de la plateforme (Dashboard Admin)
    """
    # Vérification admin (temporaire - à améliorer)
    if not request.user.is_superuser:
        return Response(
            {"error": "Seuls les administrateurs peuvent accéder aux statistiques"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # 📊 STATISTIQUES PROJETS
    projets_stats = {
        "total": Projet.objects.count(),
        "en_attente": Projet.objects.filter(statut="en_attente").count(),
        "actifs": Projet.objects.filter(statut="actif").count(),
        "finances": Projet.objects.filter(statut="finance").count(),
        "rejetes": Projet.objects.filter(statut="rejete").count(),
    }

    # 👥 STATISTIQUES UTILISATEURS
    users_stats = {
        "total": User.objects.count(),
        "contributeurs": User.objects.filter(type_utilisateur="contributeur").count(),
        "porteurs": User.objects.filter(type_utilisateur="porteur").count(),
        "admins": User.objects.filter(type_utilisateur="admin").count(),
        "nouveaux_30j": User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }

    # 💰 STATISTIQUES FINANCIÈRES (si vous avez le modèle Contribution)
    try:
        from apps.contributions.models import Contribution

        contributions_stats = {
            "total_contributions": Contribution.objects.filter(
                statut_paiement="confirme"
            ).count(),
            "montant_total": Contribution.objects.filter(
                statut_paiement="confirme"
            ).aggregate(total=Sum("montant"))["total"]
            or 0,
            "contributions_30j": Contribution.objects.filter(
                date_contribution__gte=timezone.now() - timedelta(days=30),
                statut_paiement="confirme",
            ).count(),
        }
    except ImportError:
        # Si le modèle Contribution n'existe pas encore
        contributions_stats = {
            "total_contributions": 0,
            "montant_total": 0,
            "contributions_30j": 0,
        }

    # 🎯 STATISTIQUES CATÉGORIES
    categories_populaires = (
        Categorie.objects.filter(est_active=True)
        .annotate(nb_projets=Count("projet"))
        .order_by("-nb_projets")[:5]
    )

    # 📈 PROJETS RÉCENTS EN ATTENTE (pour action rapide)
    projets_en_attente = Projet.objects.filter(statut="en_attente").order_by(
        "date_soumission"
    )[:5]

    # 🔔 CONSTRUIRE LA RÉPONSE
    stats_data = {
        "projets": projets_stats,
        "utilisateurs": users_stats,
        "contributions": contributions_stats,
        "categories_populaires": [
            {
                "nom": cat.nom,
                "icone": cat.icone,
                "nb_projets": cat.nb_projets,  # type: ignore
            }
            for cat in categories_populaires
        ],
        "projets_en_attente": ProjetListSerializer(projets_en_attente, many=True).data,
        "derniere_mise_a_jour": timezone.now().isoformat(),
    }

    return Response({"stats": stats_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # TODO: Changer en IsAdminUser plus tard
def admin_users_list_view(request):
    """
    API pour lister tous les utilisateurs (Gestion Admin)
    """
    # Vérification admin
    if not request.user.is_superuser:
        return Response(
            {"error": "Accès admin requis"}, status=status.HTTP_403_FORBIDDEN
        )

    # Filtres optionnels
    type_utilisateur = request.GET.get("type", None)
    statut = request.GET.get("statut", None)

    queryset = User.objects.all().order_by("-date_joined")

    if type_utilisateur:
        queryset = queryset.filter(type_utilisateur=type_utilisateur)

    if statut:
        queryset = queryset.filter(statut_compte=statut)

    # Pagination simple
    page = int(request.GET.get("page", 1))
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page

    users = queryset[start:end]
    total = queryset.count()

    # Sérialiser les données utilisateurs (version admin)
    users_data = []
    for user in users:
        users_data.append(
            {
                "id": user.id,  # type: ignore
                "email": user.email,
                "nom_complet": user.get_full_name(),
                "username": user.username,
                "type_utilisateur": user.type_utilisateur,  # type: ignore
                "region": user.region,  # type: ignore
                "ville": user.ville,  # type: ignore
                "statut_compte": user.statut_compte,  # type: ignore
                "date_inscription": user.date_joined,
                "derniere_connexion": user.date_derniere_connexion,  # type: ignore
                "is_active": user.is_active,
            }
        )

    return Response(
        {
            "users": users_data,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
            },
        }
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def admin_user_update_view(request, user_id):
    """
    API pour modifier un utilisateur (suspension/activation)
    Réservé aux administrateurs
    """
    # Vérification admin
    if not request.user.is_superuser:
        return Response(
            {"error": "Accès admin requis"}, status=status.HTTP_403_FORBIDDEN
        )

    # Récupérer l'utilisateur
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND
        )

    # On ne peut pas modifier un autre admin
    if user.is_superuser:
        return Response(
            {"error": "Impossible de modifier un administrateur"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Modifier le statut du compte
    statut_compte = request.data.get("statut_compte")
    if statut_compte:
        user.statut_compte = statut_compte
        # Mettre à jour is_active en fonction du statut
        if statut_compte == "suspendu":
            user.is_active = False
        elif statut_compte == "actif":
            user.is_active = True

    user.save()

    return Response(
        {
            "message": f"Utilisateur {'activé' if user.is_active else 'suspendu'} avec succès",
            "user": {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "statut_compte": user.statut_compte,
            },
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def projet_stats_view(request, projet_id):
    """
    API pour récupérer les statistiques détaillées d'un projet
    Accessible uniquement au porteur du projet
    """
    # Récupérer le projet et vérifier que l'utilisateur est le porteur
    projet = get_object_or_404(Projet, id=projet_id, porteur=request.user)
    
    # Récupérer les stats depuis les modèles existants
    from apps.interactions.models import Commentaire, Favori, Partage
    
    # Partages par plateforme
    partages_data = {}
    plateformes = ['facebook', 'twitter', 'whatsapp', 'linkedin']
    for plateforme in plateformes:
        count = Partage.objects.filter(
            projet=projet, 
            plateforme=plateforme
        ).count()
        if count > 0:
            partages_data[plateforme] = count
    
    stats = {
        # Vues (déjà dans le modèle)
        'vues': projet.nombre_vues or 0,
        
        # Partages par plateforme
        'partages': partages_data,
        
        # Commentaires (non masqués)
        'commentaires': Commentaire.objects.filter(
            projet=projet,
            est_masque=False
        ).count(),
        
        # Favoris
        'favoris': Favori.objects.filter(projet=projet).count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def upload_document_view(request, pk):
    """Upload document budget ou business plan"""
    try:
        projet = Projet.objects.get(pk=pk, porteur=request.user)
        
        # Bloquer l'upload pour les projets actifs ou en attente
        if projet.statut in ["actif", "en_attente"]:
            return Response(
                {'error': 'Les documents ne peuvent plus être modifiés pour un projet en attente de validation ou actif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 'document_budget' in request.FILES:
            projet.document_budget = request.FILES['document_budget']
        
        if 'document_business_plan' in request.FILES:
            projet.document_business_plan = request.FILES['document_business_plan']
        
        projet.save()
        
        serializer = ProjetDetailSerializer(projet)
        return Response(serializer.data)
    except Projet.DoesNotExist:
        return Response(
            {'error': 'Projet non trouvé ou vous n\'êtes pas le porteur'},
            status=status.HTTP_404_NOT_FOUND
        )

>>>>>>> ancienne_version
