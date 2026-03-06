from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Commentaire, Favori, Partage

User = get_user_model()


class CommentaireCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un commentaire"""

    class Meta:
        model = Commentaire
        fields = ["projet", "contenu", "commentaire_parent"]

    def validate_commentaire_parent(self, value):
        """Vérifier qu'on ne répond pas à une réponse"""
        if value and value.commentaire_parent is not None:
            raise serializers.ValidationError(
                "Impossible de répondre à une réponse. Répondez au commentaire principal."
            )
        return value

    def create(self, validated_data):
        validated_data["auteur"] = self.context["request"].user
        return super().create(validated_data)


class CommentaireSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les commentaires"""

    auteur_nom = serializers.CharField(source="auteur.get_full_name", read_only=True)
    auteur_photo = serializers.SerializerMethodField()
    est_reponse_porteur = serializers.ReadOnlyField()
    est_reponse = serializers.ReadOnlyField()
    peut_repondre = serializers.ReadOnlyField()
    reponses = serializers.SerializerMethodField()

    class Meta:
        model = Commentaire
        fields = [
            "id",
            "contenu",
            "auteur_nom",
            "auteur_photo",
            "est_reponse_porteur",
            "est_reponse",
            "peut_repondre",
            "date_creation",
            "date_modification",
            "reponses",
        ]

    def get_auteur_photo(self, obj):
        if obj.auteur.photo_profil:
            return obj.auteur.photo_profil.url
        return None

    def get_reponses(self, obj):
        # Seulement les réponses directes (pas de réponse à une réponse)
        if obj.commentaire_parent is None:
            reponses = obj.reponses.filter(est_masque=False).order_by("date_creation")
            return CommentaireSerializer(reponses, many=True, context=self.context).data
        return []


class FavoriSerializer(serializers.ModelSerializer):
    """Serializer pour les favoris"""

    projet = serializers.SerializerMethodField()

    class Meta:
        model = Favori
        fields = ["id", "projet", "date_ajout"]
        read_only_fields = ["id", "date_ajout"]

    def get_projet(self, obj):
        from apps.projects.serializers import ProjetListSerializer

        return ProjetListSerializer(obj.projet).data


class PartageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour enregistrer un partage"""

    class Meta:
        model = Partage
        fields = ["projet", "plateforme"]

    def create(self, validated_data):
        # L'utilisateur peut être None (partage anonyme)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["utilisateur"] = request.user
        return super().create(validated_data)


from .models import Signalement


class SignalementCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un signalement"""

    class Meta:
        model = Signalement
        fields = ["type_signalement", "objet_signale_id", "motif", "description"]

    def create(self, validated_data):
        validated_data["auteur"] = self.context["request"].user
        return super().create(validated_data)


class SignalementListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les signalements (admin)"""

    auteur_nom = serializers.CharField(source="auteur.get_full_name", read_only=True)
    motif_display = serializers.CharField(source="get_motif_display", read_only=True)
    type_display = serializers.CharField(
        source="get_type_signalement_display", read_only=True
    )
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = Signalement
        fields = [
            "id",
            "auteur_nom",
            "type_display",
            "motif_display",
            "description",
            "statut_display",
            "date_signalement",
        ]
