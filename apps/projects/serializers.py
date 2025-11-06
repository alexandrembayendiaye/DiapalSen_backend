from rest_framework import serializers
from .models import Categorie


class CategorieSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de projets"""

    nombre_projets = serializers.ReadOnlyField()

    class Meta:
        model = Categorie
        fields = [
            "id",
            "nom",
            "description",
            "icone",
            "ordre_affichage",
            "est_active",
            "nombre_projets",
        ]
        read_only_fields = ["id"]


class CategorieListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes de catégories"""

    class Meta:
        model = Categorie
        fields = ["id", "nom", "icone", "ordre_affichage"]
