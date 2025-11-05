from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


# ============================================================
# Gestionnaire d’utilisateurs : permet la création via email
# ============================================================
class UtilisateurManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Crée et enregistre un utilisateur avec l'email et le mot de passe donnés.
        """
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Crée un utilisateur standard.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée un superutilisateur (admin).
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# ============================================================
# Modèle principal : Utilisateur
# ============================================================
class Utilisateur(AbstractUser):
    # Suppression du champ username par défaut
    username = None

    # Identifiant principal
    email = models.EmailField(_("adresse email"), unique=True)

    # Informations personnelles
    first_name = models.CharField(_("Prénom"), max_length=150)
    last_name = models.CharField(_("Nom"), max_length=150)
    date_de_naissance = models.DateField(_("Date de naissance"), null=True, blank=True)

    numero_telephone = models.CharField(
        _("Numéro de téléphone"),
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^[0-9+\- ]+$", "Numéro invalide.")],
    )

    adresse = models.CharField(_("Adresse"), max_length=255, null=True, blank=True)
    ville = models.CharField(_("Ville"), max_length=100, null=True, blank=True)

    # Rôle / Type d'utilisateur
    TYPE_UTILISATEUR = [
        ("standard", "Contributeur standard"),
        ("porteur", "Porteur de projet"),
        ("admin", "Administrateur"),
    ]
    type_utilisateur = models.CharField(
        _("Type d'utilisateur"),
        max_length=20,
        choices=TYPE_UTILISATEUR,
        default="standard",
    )

    # Photo de profil (upload dans media/profiles/)
    photo_profil = models.ImageField(
        _("Photo de profil"), upload_to="profiles/", null=True, blank=True
    )

    # Champs obligatoires pour AbstractUser
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Lien vers le gestionnaire
    objects = UtilisateurManager()  # type: ignore

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
