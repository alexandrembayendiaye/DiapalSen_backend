from rest_framework import serializers
from .models import Project
from .models import Project, Categorie


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["id", "nom", "description", "icone", "est_active", "ordre_affichage"]


class ProjectSerializer(serializers.ModelSerializer):
    """
    Sérialiseur principal pour le modèle Project.
    Convertit un projet en JSON et gère la validation à la création / mise à jour.
    """

    # Champs en lecture seule (non modifiables depuis une requête POST/PUT)
    porteur_nom = serializers.CharField(source="porteur.first_name", read_only=True)
    porteur_prenom = serializers.CharField(source="porteur.last_name", read_only=True)
    email_porteur = serializers.EmailField(source="porteur.email", read_only=True)
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "titre",
            "description",
            "montant_objectif",
            "montant_actuel",
            "categorie",
            "categorie_id",
            "statut",
            "porteur",
            "porteur_nom",
            "porteur_prenom",
            "email_porteur",
            "image_couverture",
            "date_creation",
            "date_mise_a_jour",
        ]
        read_only_fields = [
            "id",
            "montant_actuel",
            "date_creation",
            "date_mise_a_jour",
            "statut",
        ]

    def validate_montant_objectif(self, value):
        """
        Validation du montant : doit être supérieur à 0.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "Le montant objectif doit être supérieur à 0."
            )
        return value

    def create(self, validated_data):
        """
        Crée un projet en associant la catégorie correcte
        et en laissant la vue injecter le porteur.
        """
        categorie_id = validated_data.pop("categorie_id")
        categorie = Categorie.objects.get(id=categorie_id)

        # On crée le projet sans définir porteur ici
        return Project.objects.create(categorie=categorie, **validated_data)


from rest_framework import serializers
from .models import Project


class ProjectStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["statut"]  # On ne modifie que le statut

    def validate_statut(self, value):
        """
        Valide la cohérence de la transition de statut.
        """
        projet = getattr(self, "instance", None)
        if not projet:
            return value  # Cas sécurité : création, normalement jamais utilisé ici

        user = self.context["request"].user

        # Règles métier simples :
        if projet.statut == "brouillon" and value not in ["en_attente"]:
            raise serializers.ValidationError(
                "Un projet en brouillon ne peut être soumis qu'en attente de validation."
            )

        if projet.statut == "en_attente" and value not in ["valide", "rejete"]:
            raise serializers.ValidationError(
                "Un projet en attente ne peut être que validé ou rejeté."
            )

        if projet.statut in ["valide", "rejete", "termine"]:
            raise serializers.ValidationError(
                "Impossible de modifier le statut d’un projet déjà finalisé."
            )

        return value
