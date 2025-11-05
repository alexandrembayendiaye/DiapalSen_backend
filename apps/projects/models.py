import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal
from uuid import uuid4


class Project(models.Model):
    """
    Représente un projet de crowdfunding sur DiapalSen.
    """

    # Identifiant unique (clé primaire UUID)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Informations principales
    titre = models.CharField(max_length=255)
    description = models.TextField()

    # Financement
    montant_objectif = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Montant total à collecter (en FCFA).",
    )
    montant_actuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Montant déjà collecté.",
    )

    # Catégorie (sera liée plus tard à une table Categorie)
    categorie = models.ForeignKey(
        "Categorie", on_delete=models.SET_NULL, null=True, related_name="projets"
    )

    # Statut du projet
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("en_attente", "En attente de validation"),
        ("valide", "Validé"),
        ("rejete", "Rejeté"),
        ("termine", "Terminé"),
    ]
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="brouillon"
    )

    # Porteur de projet (relation vers le modèle Utilisateur)
    porteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mes_projets",
    )

    # Image de couverture
    image_couverture = models.ImageField(
        upload_to="projects/covers/", blank=True, null=True
    )

    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


class Categorie(models.Model):
    """
    Représente une catégorie de projet (ex: Agriculture, Santé, etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icone = models.CharField(max_length=100, blank=True, null=True)
    est_active = models.BooleanField(default=True)
    ordre_affichage = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ["ordre_affichage", "nom"]
