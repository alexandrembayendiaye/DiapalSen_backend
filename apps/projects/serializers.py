from rest_framework import serializers
from .models import Categorie
from django.contrib.auth import get_user_model
from .models import Projet


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


User = get_user_model()


class ProjetCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un projet (brouillon)"""

    class Meta:
        model = Projet
        fields = [
            "id",
            "titre",
            "description_courte",
            "description_complete",
            "categorie",
            "region",
            "ville",
            "montant_objectif",
            "duree_campagne_jours",
            "image_principale",
            "video_url",
            "document_budget",
            "document_business_plan",
        ]

    def create(self, validated_data):
        # Le porteur est automatiquement l'utilisateur connecté
        validated_data["porteur"] = self.context["request"].user
        validated_data["statut"] = "brouillon"
        return super().create(validated_data)


class ProjetListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des projets (vue publique)"""

    porteur_nom = serializers.CharField(source="porteur.get_full_name", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)
    categorie_icone = serializers.CharField(source="categorie.icone", read_only=True)
    pourcentage_atteint = serializers.ReadOnlyField()
    jours_restants = serializers.ReadOnlyField()

    class Meta:
        model = Projet
        fields = [
            "id",
            "titre",
            "description_courte",
            "image_principale",
            "montant_objectif",
            "montant_collecte",
            "pourcentage_atteint",
            "nombre_contributeurs",
            "jours_restants",
            "statut",
            "porteur_nom",
            "categorie_nom",
            "categorie_icone",
            "region",
            "ville",
            "date_creation",
        ]


class ProjetDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail complet d'un projet"""

    porteur = serializers.SerializerMethodField()
    categorie = CategorieListSerializer(read_only=True)
    pourcentage_atteint = serializers.ReadOnlyField()
    jours_restants = serializers.ReadOnlyField()
    est_finance = serializers.ReadOnlyField()

    class Meta:
        model = Projet
        fields = [
            "id",
            "titre",
            "description_courte",
            "description_complete",
            "image_principale",
            "video_url",
            "montant_objectif",
            "montant_collecte",
            "pourcentage_atteint",
            "nombre_contributeurs",
            "jours_restants",
            "est_finance",
            "statut",
            "porteur",
            "categorie",
            "region",
            "ville",
            "type_financement",
            "duree_campagne_jours",
            "date_debut_campagne",
            "date_fin_campagne",
            "document_budget",
            "document_business_plan",
            "nombre_vues",
            "date_creation",
        ]

    def get_porteur(self, obj):
        return {
            "id": obj.porteur.id,
            "nom_complet": obj.porteur.get_full_name(),
            "photo_profil": (
                obj.porteur.photo_profil.url if obj.porteur.photo_profil else None
            ),
        }


class ProjetUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la modification d'un projet (par le porteur)"""

    class Meta:
        model = Projet
        fields = [
            "titre",
            "description_courte",
            "description_complete",
            "categorie",
            "montant_objectif",
            "type_financement",
            "region",
            "ville",
            "image_principale",
            "video_url",
            "document_budget",
            "document_business_plan",
            "date_debut_campagne",
            "date_fin_campagne",
        ]

    def validate(self, data):
        """Validation selon le statut du projet"""
        projet = self.instance
        
        if not projet:
            return data
        
        # Projets terminés ou rejetés : aucune modification
        if projet.statut in ['termine', 'rejete']:
            raise serializers.ValidationError(
                "Ce projet ne peut plus être modifié (statut: {})".format(projet.statut)
            )
        
        # Projet actif : seulement description complète et vidéo
        if projet.statut == 'actif':
            champs_autorises = {'description_complete', 'video_url'}
            champs_modifies = set(data.keys())
            champs_interdits = champs_modifies - champs_autorises
            
            if champs_interdits:
                raise serializers.ValidationError({
                    list(champs_interdits)[0]: 
                    f"Ce champ ne peut pas être modifié pour un projet actif. "
                    f"Seuls 'description_complete' et 'video_url' sont modifiables."
                })
        
        # Projet en attente : champs limités
        elif projet.statut == 'en_attente':
            champs_interdits = {
                'titre', 'montant_objectif', 'categorie', 
                'date_debut_campagne', 'date_fin_campagne', 'type_financement'
            }
            champs_modifies = set(data.keys())
            champs_non_autorises = champs_modifies & champs_interdits
            
            if champs_non_autorises:
                raise serializers.ValidationError({
                    list(champs_non_autorises)[0]: 
                    f"Ce champ ne peut pas être modifié pour un projet en attente de validation."
                })
        
        # Brouillon : tous les champs modifiables (pas de restriction)
        
        return data


from .models import ValidationProjet


class ValidationProjetSerializer(serializers.ModelSerializer):
    """Serializer pour les validations de projets"""

    administrateur_nom = serializers.CharField(
        source="administrateur.get_full_name", read_only=True
    )
    projet_titre = serializers.CharField(source="projet.titre", read_only=True)

    class Meta:
        model = ValidationProjet
        fields = [
            "id",
            "decision",
            "type_financement_choisi",
            "commentaire",
            "motif_rejet",
            "date_validation",
            "administrateur_nom",
            "projet_titre",
        ]
        read_only_fields = ["id", "date_validation"]


class ProjetValidationSerializer(serializers.Serializer):
    """Serializer pour valider/rejeter un projet"""

    decision = serializers.ChoiceField(choices=ValidationProjet.DECISION_CHOICES)
    type_financement = serializers.ChoiceField(
        choices=Projet.TYPE_FINANCEMENT_CHOICES,
        required=False,
        help_text="Requis si decision=approuve",
    )
    commentaire = serializers.CharField(
        max_length=1000, help_text="Commentaire de l'administrateur"
    )
    motif_rejet = serializers.CharField(
        max_length=1000, required=False, help_text="Requis si decision=rejete"
    )

    def validate(self, attrs):
        decision = attrs.get("decision")

        if decision == "approuve" and not attrs.get("type_financement"):
            raise serializers.ValidationError(
                {
                    "type_financement": "Le type de financement est requis pour approuver un projet."
                }
            )

        if decision == "rejete" and not attrs.get("motif_rejet"):
            raise serializers.ValidationError(
                {"motif_rejet": "Le motif de rejet est requis pour rejeter un projet."}
            )

        return attrs
