from rest_framework import serializers
<<<<<<< HEAD
from .models import Contribution
from apps.projects.models import Project


class ContributionSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création et la lecture des contributions.
    """

    # On affiche le titre du projet dans les réponses (lecture)
    projet_titre = serializers.CharField(source="projet.titre", read_only=True)
=======
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
>>>>>>> ancienne_version

    class Meta:
        model = Contribution
        fields = [
            "id",
<<<<<<< HEAD
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
=======
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
>>>>>>> ancienne_version
