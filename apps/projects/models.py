from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Categorie(models.Model):
    """
    Modèle pour les catégories de projets DiapalSen
    """

    nom = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom de la catégorie (ex: Agriculture & Élevage)",
    )

    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Description détaillée de la catégorie",
    )

    icone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Code emoji ou classe CSS pour l'icône (ex: 🌾, fa-seedling)",
    )

    ordre_affichage = models.PositiveIntegerField(
        default=0, help_text="Ordre d'affichage dans les listes (0 = premier)"
    )

    est_active = models.BooleanField(
        default=True, help_text="Catégorie visible et utilisable"
    )

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["ordre_affichage", "nom"]

    def __str__(self):
        return f"{self.icone} {self.nom}" if self.icone else self.nom

    @property
    def nombre_projets(self):
        """Retourne le nombre de projets actifs dans cette catégorie"""
        # À implémenter plus tard quand on aura le modèle Projet
        return 0


User = get_user_model()


class Projet(models.Model):
    """
    Modèle pour les projets de crowdfunding DiapalSen
    """

    # Choix pour les régions (même que User)
    REGION_CHOICES = [
        ("dakar", "Dakar"),
        ("thies", "Thiès"),
        ("saint-louis", "Saint-Louis"),
        ("diourbel", "Diourbel"),
        ("louga", "Louga"),
        ("fatick", "Fatick"),
        ("kaolack", "Kaolack"),
        ("kolda", "Kolda"),
        ("matam", "Matam"),
        ("tambacounda", "Tambacounda"),
        ("kaffrine", "Kaffrine"),
        ("kedougou", "Kédougou"),
        ("sedhiou", "Sédhiou"),
        ("ziguinchor", "Ziguinchor"),
    ]

    # Types de financement
    TYPE_FINANCEMENT_CHOICES = [
        ("tout_ou_rien", "Tout ou rien (100%)"),
        ("flexible_50", "Flexible 50% minimum"),
        ("solidaire", "Solidaire (0% minimum)"),
    ]

    # Statuts des projets
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("en_attente", "En attente de validation"),
        ("rejete", "Rejeté"),
        ("actif", "Campagne active"),
        ("finance", "Financé avec succès"),
        ("non_finance", "Non financé"),
        ("suspendu", "Suspendu"),
        ("archive", "Archivé"),
    ]

    # Relations
    porteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projets_crees",
        help_text="Utilisateur qui a créé le projet",
    )

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name="projets",
        help_text="Catégorie du projet",
    )

    # Informations de base
    titre = models.CharField(max_length=200, help_text="Titre accrocheur du projet")

    description_courte = models.TextField(
        max_length=300, help_text="Résumé en quelques lignes"
    )

    description_complete = models.TextField(help_text="Description détaillée du projet")

    # Localisation
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        help_text="Région de réalisation du projet",
    )

    ville = models.CharField(
        max_length=100, help_text="Ville ou commune de réalisation"
    )

    # Financement
    montant_objectif = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[
            MinValueValidator(100000),  # 100k FCFA minimum
            MaxValueValidator(10000000),  # 10M FCFA maximum
        ],
        help_text="Montant à collecter en FCFA (100k à 10M)",
    )

    montant_collecte = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=Decimal("0"),
        help_text="Montant actuellement collecté",
    )

    nombre_contributeurs = models.PositiveIntegerField(
        default=0, help_text="Nombre de personnes ayant contribué"
    )

    type_financement = models.CharField(
        max_length=20,
        choices=TYPE_FINANCEMENT_CHOICES,
        blank=True,
        null=True,
        help_text="Type défini par l'administrateur lors de la validation",
    )

    commentaire_admin_financement = models.TextField(
        blank=True,
        null=True,
        help_text="Commentaire de l'admin sur le choix du type de financement",
    )

    # Durée de campagne
    duree_campagne_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(7), MaxValueValidator(90)],
        help_text="Durée de la campagne en jours (7 à 90)",
    )

    # Dates importantes
    date_soumission = models.DateTimeField(
        blank=True, null=True, help_text="Date de soumission pour validation"
    )

    date_validation = models.DateTimeField(
        blank=True, null=True, help_text="Date de validation par l'admin"
    )

    date_debut_campagne = models.DateTimeField(
        blank=True, null=True, help_text="Date de début de la campagne"
    )

    date_fin_campagne = models.DateTimeField(
        blank=True, null=True, help_text="Date de fin de la campagne"
    )

    # Statut et validation
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="brouillon",
        help_text="Statut actuel du projet",
    )

    motif_rejet = models.TextField(
        blank=True, null=True, help_text="Motif de rejet par l'administrateur"
    )

    # Médias
    image_principale = models.ImageField(
        upload_to="projects/",
        blank=True,
        null=True,
        help_text="Image principale du projet",
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL de la vidéo de présentation (YouTube, Vimeo)",
    )

    # Documents
    document_budget = models.FileField(
        upload_to="projects/documents/",
        blank=True,
        null=True,
        help_text="Document de budget prévisionnel",
    )

    document_business_plan = models.FileField(
        upload_to="projects/documents/",
        blank=True,
        null=True,
        help_text="Business plan ou note de présentation",
    )

    # Statistiques
    nombre_vues = models.PositiveIntegerField(
        default=0, help_text="Nombre de consultations du projet"
    )

    nombre_partages = models.PositiveIntegerField(
        default=0, help_text="Nombre de partages sur réseaux sociaux"
    )

    fonds_debloques = models.BooleanField(
        default=False, help_text="Fonds débloqués au porteur de projet"
    )

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["statut", "-date_creation"], name="projet_statut_date_idx"),
            models.Index(fields=["region", "categorie"], name="projet_region_cat_idx"),
            models.Index(fields=["porteur", "statut"], name="projet_porteur_statut_idx"),
            models.Index(fields=["categorie", "statut"], name="projet_cat_statut_idx"),
            models.Index(fields=["-date_debut_campagne"], name="projet_debut_camp_idx"),
        ]

    def __str__(self):
        return f"{self.titre} - {self.get_statut_display()}"  # pyright: ignore[reportAttributeAccessIssue]

    @property
    def pourcentage_atteint(self):
        """Calcule le pourcentage de l'objectif atteint"""
        if self.montant_objectif > 0:
            return round(
                (float(self.montant_collecte) / float(self.montant_objectif)) * 100, 1
            )
        return 0

    @property
    def est_finance(self):
        """Détermine si le projet est financé selon son type"""
        pourcentage = self.pourcentage_atteint

        if self.type_financement == "tout_ou_rien":
            return pourcentage >= 100
        elif self.type_financement == "flexible_50":
            return pourcentage >= 50
        elif self.type_financement == "solidaire":
            return pourcentage > 0

        return False

    @property
    def jours_restants(self):
        """Calcule le nombre de jours restants pour la campagne"""
        if self.date_fin_campagne and self.statut == "actif":
            from django.utils import timezone

            delta = self.date_fin_campagne - timezone.now()
            return max(0, delta.days)
        return 0


class ValidationProjet(models.Model):
    """
    Modèle pour tracer les validations/rejets de projets par les admins
    """

    DECISION_CHOICES = [
        ("approuve", "Approuvé"),
        ("rejete", "Rejeté"),
        ("infos_demandees", "Informations demandées"),
    ]

    projet = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name="validations",
        help_text="Projet concerné par la validation",
    )

    administrateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="validations_effectuees",
        help_text="Administrateur qui a pris la décision",
    )

    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        help_text="Décision prise par l'administrateur",
    )

    type_financement_choisi = models.CharField(
        max_length=20,
        choices=Projet.TYPE_FINANCEMENT_CHOICES,
        blank=True,
        null=True,
        help_text="Type de financement choisi si approuvé",
    )

    commentaire = models.TextField(help_text="Commentaire de l'administrateur")

    motif_rejet = models.TextField(
        blank=True, null=True, help_text="Motifs détaillés en cas de rejet"
    )

    date_validation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Validation de projet"
        verbose_name_plural = "Validations de projets"
        ordering = ["-date_validation"]

    def __str__(self):
        return f"{self.projet.titre} - {self.get_decision_display()} par {self.administrateur.get_full_name()}"  # type: ignore


class MiseAJourProjet(models.Model):
    """
    Modèle pour les mises à jour publiées par les porteurs de projet
    """

    VISIBILITE_CHOICES = [
        ("public", "Public (visible par tous)"),
        ("contributeurs", "Contributeurs uniquement"),
    ]

    projet = models.ForeignKey(
        Projet,
        on_delete=models.CASCADE,
        related_name="mises_a_jour",
        help_text="Projet concerné par la mise à jour",
    )

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mises_a_jour_publiees",
        help_text="Auteur de la mise à jour (normalement le porteur)",
    )

    titre = models.CharField(max_length=200, help_text="Titre de la mise à jour")

    contenu = models.TextField(help_text="Contenu détaillé de la mise à jour")

    images = models.ImageField(
        upload_to="mises_a_jour/",
        blank=True,
        null=True,
        help_text="Images illustrant la mise à jour",
    )

    visibilite = models.CharField(
        max_length=20,
        choices=VISIBILITE_CHOICES,
        default="public",
        help_text="Qui peut voir cette mise à jour",
    )

    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mise à jour de projet"
        verbose_name_plural = "Mises à jour de projets"
        ordering = ["-date_publication"]

    def __str__(self):
        return f"Mise à jour: {self.titre} - {self.projet.titre}"

    def peut_voir(self, utilisateur):
        """Détermine si un utilisateur peut voir cette mise à jour"""
        if self.visibilite == "public":
            return True
        elif self.visibilite == "contributeurs":
            # Vérifier si l'utilisateur a contribué au projet
            from apps.contributions.models import Contribution

            return Contribution.objects.filter(
                projet=self.projet, contributeur=utilisateur, statut_paiement="valide"
            ).exists()
        return False
