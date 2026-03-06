from rest_framework import serializers
<<<<<<< HEAD
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
=======
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

    porteur_nom = serializers.SerializerMethodField()
    porteur_email = serializers.EmailField(source="porteur.email", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)
    categorie_icone = serializers.CharField(source="categorie.icone", read_only=True)
    pourcentage_atteint = serializers.ReadOnlyField()
    jours_restants = serializers.ReadOnlyField()
    commentaire_admin = serializers.SerializerMethodField()

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
            "porteur_email",
            "categorie_nom",
            "categorie_icone",
            "region",
            "ville",
            "date_creation",
            "date_soumission",
            "motif_rejet",
            "commentaire_admin",
        ]

    def get_porteur_nom(self, obj):
        """Retourne le nom complet du porteur ou son username en fallback"""
        full_name = obj.porteur.get_full_name()
        return full_name if full_name else obj.porteur.username

    def get_commentaire_admin(self, obj):
        """Retourne le commentaire de la dernière validation admin"""
        from .models import ValidationProjet
        derniere_validation = ValidationProjet.objects.filter(projet=obj).order_by('-date_validation').first()
        if derniere_validation:
            return derniere_validation.commentaire
        return None


class ProjetDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail complet d'un projet"""

    porteur = serializers.SerializerMethodField()
    porteur_nom = serializers.SerializerMethodField()
    porteur_email = serializers.EmailField(source="porteur.email", read_only=True)
    categorie = CategorieListSerializer(read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)
    categorie_icone = serializers.CharField(source="categorie.icone", read_only=True)
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
            "porteur_nom",
            "porteur_email",
            "categorie",
            "categorie_nom",
            "categorie_icone",
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
            "date_soumission",
        ]

    def get_porteur_nom(self, obj):
        """Retourne le nom complet du porteur ou son username en fallback"""
        full_name = obj.porteur.get_full_name()
        return full_name if full_name else obj.porteur.username

    def get_porteur(self, obj):
        return {
            "id": obj.porteur.id,
            "nom_complet": obj.porteur.get_full_name() or obj.porteur.username,
            "email": obj.porteur.email,
            "telephone": getattr(obj.porteur, 'telephone', None),
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
            "projet",
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
>>>>>>> ancienne_version
