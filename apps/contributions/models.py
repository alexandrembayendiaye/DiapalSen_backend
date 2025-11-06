import uuid
from django.db import models
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
