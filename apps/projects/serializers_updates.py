from rest_framework import serializers
from .models import MiseAJourProjet


class MiseAJourProjetCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une mise à jour de projet"""

    class Meta:
        model = MiseAJourProjet
        fields = ["titre", "contenu", "images", "visibilite"]

    def create(self, validated_data):
        validated_data["auteur"] = self.context["request"].user
        validated_data["projet"] = self.context["projet"]
        return super().create(validated_data)


class MiseAJourProjetSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les mises à jour"""

    auteur_nom = serializers.CharField(source="auteur.get_full_name", read_only=True)

    class Meta:
        model = MiseAJourProjet
        fields = [
            "id",
            "titre",
            "contenu",
            "images",
            "visibilite",
            "auteur_nom",
            "date_publication",
        ]
