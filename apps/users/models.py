from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Modèle User personnalisé pour DiapalSen
    Étend AbstractUser avec les champs spécifiques du projet
    """

    # Choix pour le type d'utilisateur
    TYPE_CHOICES = [
        ("contributeur", "Contributeur"),
        ("porteur", "Porteur de projet"),
        ("admin", "Administrateur"),
    ]

    # Choix pour les régions du Sénégal
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

    # Choix pour le statut du compte
    STATUT_CHOICES = [
        ("actif", "Actif"),
        ("suspendu", "Suspendu"),
        ("supprime", "Supprimé"),
    ]

    # Validateur pour le téléphone (format sénégalais)
    phone_validator = RegexValidator(
        regex=r"^\+221[0-9]{9}$|^[0-9]{9}$",
        message="Le numéro de téléphone doit être au format sénégalais.",
    )

    # Champs personnalisés
    telephone = models.CharField(
        max_length=15,
        validators=[phone_validator],
        blank=True,
        null=True,
        help_text="Format: +221xxxxxxxxx ou xxxxxxxxx",
    )

    type_utilisateur = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="contributeur",
        help_text="Type de compte utilisateur",
    )

    photo_profil = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        help_text="Photo de profil de l'utilisateur",
    )

    biographie = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Courte biographie de l'utilisateur",
    )

    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        blank=True,
        null=True,
        help_text="Région de résidence",
    )

    ville = models.CharField(
        max_length=100, blank=True, null=True, help_text="Ville ou commune de résidence"
    )

    date_derniere_connexion = models.DateTimeField(
        blank=True, null=True, help_text="Date et heure de la dernière connexion"
    )

    statut_compte = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="actif",
        help_text="Statut du compte utilisateur",
    )

    # Métadonnées
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_contributeur(self):
        return self.type_utilisateur == "contributeur"

    @property
    def is_porteur(self):
        return self.type_utilisateur == "porteur"

    @property
    def is_admin_custom(self):
        return self.type_utilisateur == "admin" or self.is_superuser
