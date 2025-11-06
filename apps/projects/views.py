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
