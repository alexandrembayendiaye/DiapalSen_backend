from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """
    Modèle pour les notifications utilisateurs
    """

    TYPE_NOTIFICATION_CHOICES = [
        # Notifications porteur
        ("projet_valide", "Projet validé"),
        ("projet_rejete", "Projet rejeté"),
        ("infos_demandees", "Modification demandée"),
        ("nouvelle_contribution", "Nouvelle contribution reçue"),
        ("commentaire_projet", "Nouveau commentaire sur votre projet"),
        ("objectif_atteint", "Objectif de financement atteint"),
        ("fin_campagne", "Fin de campagne"),
        # Notifications contributeur
        ("contribution_confirmee", "Contribution confirmée"),
        ("mise_a_jour_projet", "Mise à jour de projet suivi"),
        ("projet_finance", "Projet soutenu financé"),
        # Notifications admin
        ("projet_soumis", "Nouveau projet à valider"),
        # Notifications générales
        ("favori_nouveau_projet", "Nouveau projet dans catégorie favorite"),
        ("rappel_projet", "Rappel projet bientôt terminé"),
        ("bienvenue", "Bienvenue sur DiapalSen"),
    ]

    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_recues",
        help_text="Utilisateur qui reçoit la notification",
    )

    type_notification = models.CharField(
        max_length=30,
        choices=TYPE_NOTIFICATION_CHOICES,
        help_text="Type de notification",
    )

    titre = models.CharField(max_length=200, help_text="Titre de la notification")

    contenu = models.TextField(
        max_length=500, help_text="Contenu détaillé de la notification"
    )

    lien_action = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Lien vers l'élément concerné (projet, contribution, etc.)",
    )

    # Métadonnées de lecture
    est_lue = models.BooleanField(
        default=False, help_text="Notification lue par l'utilisateur"
    )

    date_lecture = models.DateTimeField(
        blank=True, null=True, help_text="Date de lecture de la notification"
    )

    # Métadonnées d'envoi email
    est_envoyee_email = models.BooleanField(
        default=False, help_text="Notification envoyée par email"
    )

    # Données contextuelles
    donnees_contextuelles = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données additionnelles (ID projet, montant, etc.)",
    )

    # Métadonnées temporelles
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["destinataire", "est_lue", "-date_creation"], name="notif_user_lue_date_idx"),
            models.Index(fields=["type_notification", "-date_creation"], name="notif_type_date_idx"),
        ]

    def __str__(self):
        status = " ✓" if self.est_lue else ""
        return f"{self.destinataire.get_full_name()} - {self.titre}{status}"

    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.est_lue:
            from django.utils import timezone

            self.est_lue = True
            self.date_lecture = timezone.now()
            self.save(update_fields=["est_lue", "date_lecture"])
