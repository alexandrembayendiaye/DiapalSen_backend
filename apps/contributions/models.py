from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

User = get_user_model()


class Contribution(models.Model):
    """
    Modèle pour les contributions financières aux projets
    """

    MOYEN_PAIEMENT_CHOICES = [
        ("wave", "Wave"),
        ("orange_money", "Orange Money"),
        ("free_money", "Free Money"),
    ]

    STATUT_PAIEMENT_CHOICES = [
        ("en_attente", "En attente"),
        ("valide", "Validé"),
        ("echoue", "Échec"),
        ("rembourse", "Remboursé"),
    ]

    # Relations
    projet = models.ForeignKey(
        "projects.Projet",
        on_delete=models.CASCADE,
        related_name="contributions",
        help_text="Projet soutenu",
    )

    contributeur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contributions_effectuees",
        help_text="Utilisateur qui contribue",
    )

    # Montant et message
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal("1000"))],  # 1000 FCFA minimum
        help_text="Montant de la contribution en FCFA (min 1000)",
    )

    message_soutien = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Message optionnel de soutien au porteur",
    )

    est_anonyme = models.BooleanField(
        default=False, help_text="Contribution anonyme (nom masqué publiquement)"
    )

    # Paiement (simulé)
    reference_paiement = models.CharField(
        max_length=100, unique=True, help_text="Référence unique de la transaction"
    )

    moyen_paiement = models.CharField(
        max_length=20,
        choices=MOYEN_PAIEMENT_CHOICES,
        help_text="Moyen de paiement choisi",
    )

    statut_paiement = models.CharField(
        max_length=20,
        choices=STATUT_PAIEMENT_CHOICES,
        default="en_attente",
        help_text="Statut de la transaction",
    )

    # Reçu PDF
    recu_pdf = models.FileField(
        upload_to="recus/",
        blank=True,
        null=True,
        help_text="Reçu PDF généré automatiquement",
    )

    # Métadonnées
    date_contribution = models.DateTimeField(auto_now_add=True)
    date_remboursement = models.DateTimeField(
        blank=True, null=True, help_text="Date de remboursement si applicable"
    )

    # Champs techniques
    donnees_paiement = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données techniques de simulation du paiement",
    )

    class Meta:
        verbose_name = "Contribution"
        verbose_name_plural = "Contributions"
        ordering = ["-date_contribution"]

    def __str__(self):
        anonyme = " (anonyme)" if self.est_anonyme else ""
        return f"{self.montant} FCFA pour {self.projet.titre} par {self.contributeur.get_full_name()}{anonyme}"

    def save(self, *args, **kwargs):
        # Générer une référence unique si pas encore définie
        if not self.reference_paiement:
            self.reference_paiement = f"DPS_{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @property
    def contributeur_nom_affiche(self):
        """Retourne le nom à afficher (respecte l'anonymat)"""
        if self.est_anonyme:
            return "Contributeur anonyme"
        return self.contributeur.get_full_name()
