from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Contribution

User = get_user_model()


class ContributionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une nouvelle contribution"""

    class Meta:
        model = Contribution
        fields = [
            "projet",
            "montant",
            "message_soutien",
            "est_anonyme",
            "moyen_paiement",
        ]

    def validate_projet(self, value):
        """Vérifier que le projet accepte encore les contributions"""
        if value.statut != "actif":
            raise serializers.ValidationError(
                "Ce projet n'accepte plus de contributions."
            )

        # Vérifier que la campagne n'est pas terminée
        if value.jours_restants <= 0:
            raise serializers.ValidationError("La campagne de ce projet est terminée.")

        return value

    def create(self, validated_data):
        # Le contributeur est automatiquement l'utilisateur connecté
        validated_data["contributeur"] = self.context["request"].user
        return super().create(validated_data)


class ContributionListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les contributions d'un projet"""

    contributeur_id = serializers.IntegerField(source="contributeur.id", read_only=True)
    contributeur_nom = serializers.CharField(
        source="contributeur_nom_affiche", read_only=True
    )
    contributeur_email = serializers.EmailField(source="contributeur.email", read_only=True)
    moyen_paiement_display = serializers.CharField(
        source="get_moyen_paiement_display", read_only=True
    )

    class Meta:
        model = Contribution
        fields = [
            "id",
            "montant",
            "message_soutien",
            "contributeur_id",
            "contributeur_nom",
            "contributeur_email",
            "moyen_paiement_display",
            "date_contribution",
            "est_anonyme",
        ]


class ContributionDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'une contribution (pour le contributeur)"""

    projet_titre = serializers.CharField(source="projet.titre", read_only=True)
    statut_paiement_display = serializers.CharField(
        source="get_statut_paiement_display", read_only=True
    )
    moyen_paiement_display = serializers.CharField(
        source="get_moyen_paiement_display", read_only=True
    )

    class Meta:
        model = Contribution
        fields = [
            "id",
            "projet_titre",
            "montant",
            "message_soutien",
            "est_anonyme",
            "reference_paiement",
            "moyen_paiement_display",
            "statut_paiement_display",
            "date_contribution",
            "recu_pdf",
        ]


class MesContributionsSerializer(serializers.ModelSerializer):
    """Serializer pour les contributions de l'utilisateur connecté"""

    projet = serializers.SerializerMethodField()
    statut_paiement_display = serializers.CharField(
        source="get_statut_paiement_display", read_only=True
    )

    class Meta:
        model = Contribution
        fields = [
            "id",
            "projet",
            "montant",
            "message_soutien",
            "reference_paiement",
            "statut_paiement_display",
            "date_contribution",
            "recu_pdf",
        ]

    def get_projet(self, obj):
        return {
            "id": obj.projet.id,
            "titre": obj.projet.titre,
            "statut": obj.projet.get_statut_display(),
            "pourcentage_atteint": obj.projet.pourcentage_atteint,
        }
