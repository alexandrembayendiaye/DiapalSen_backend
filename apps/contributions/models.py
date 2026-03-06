import uuid
from django.db import models
<<<<<<< HEAD
from django.conf import settings
from apps.projects.models import Project


class Contribution(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente de paiement"),
        ("confirmee", "Confirmée"),
        ("annulee", "Annulée"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contributeur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contributions"
    )
    projet = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributions"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_contribution = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="en_attente"
    )

    class Meta:
        verbose_name = "Contribution"
        verbose_name_plural = "Contributions"
        ordering = ["-date_contribution"]

    def __str__(self):
        return f"{self.contributeur.first_name} - {self.projet.titre} ({self.montant} FCFA)"
=======
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
        indexes = [
            models.Index(fields=["projet", "statut_paiement"], name="contrib_projet_statut_idx"),
            models.Index(fields=["contributeur", "-date_contribution"], name="contrib_user_date_idx"),
            models.Index(fields=["statut_paiement", "-date_contribution"], name="contrib_statut_date_idx"),
        ]

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

    def generer_recu(self):
        """Génère le reçu PDF pour cette contribution"""
        from .services import PDFService

        if self.statut_paiement == "valide" and not self.recu_pdf:
            try:
                PDFService.generer_recu_pdf(self)
                return True
            except Exception as e:
                print(f"Erreur génération PDF: {e}")
                return False
        return False

    def envoyer_recu_email(self):
        """Envoie le reçu PDF par email au contributeur"""
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string

        if not self.recu_pdf:
            return False

        try:
            # Préparer le contexte pour le template email
            context = {
                "contributeur": self.contributeur,
                "contribution": self,
                "projet": self.projet,
            }

            # Générer le contenu HTML de l'email
            html_content = render_to_string("emails/email_recu.html", context)

            # Créer l'email
            email = EmailMessage(
                subject=f"Reçu de contribution - {self.projet.titre}",
                body=html_content,
                from_email="noreply@diapalsen.com",
                to=[self.contributeur.email],
            )
            email.content_subtype = "html"

            # Attacher le PDF
            if self.recu_pdf:
                email.attach_file(self.recu_pdf.path)

            # Envoyer
            email.send()
            return True

        except Exception as e:
            print(f"Erreur envoi email: {e}")
            return False

>>>>>>> ancienne_version
