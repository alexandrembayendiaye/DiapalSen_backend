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
