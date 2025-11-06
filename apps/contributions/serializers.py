from rest_framework import serializers
from .models import Contribution
from apps.projects.models import Project


class ContributionSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création et la lecture des contributions.
    """

    # On affiche le titre du projet dans les réponses (lecture)
    projet_titre = serializers.CharField(source="projet.titre", read_only=True)

    class Meta:
        model = Contribution
        fields = [
            "id",
            "contributeur",
            "projet",
            "projet_titre",
            "montant",
            "date_contribution",
            "statut",
        ]
        read_only_fields = ["id", "contributeur", "date_contribution", "statut"]

    def validate_montant(self, value):
        """
        Vérifie que le montant est positif.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant doit être supérieur à 0 FCFA."
            )
        return value

    def validate_projet(self, projet):
        """
        Vérifie que le projet est éligible (statut 'valide').
        """
        if projet.statut != "valide":
            raise serializers.ValidationError(
                "Ce projet n’est pas disponible pour les contributions."
            )
        return projet

    def create(self, validated_data):
        """
        Associe automatiquement le contributeur connecté à la contribution.
        """
        user = self.context["request"].user
        contribution = Contribution.objects.create(contributeur=user, **validated_data)
        return contribution
