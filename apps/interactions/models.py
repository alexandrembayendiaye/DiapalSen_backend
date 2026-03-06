from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Commentaire(models.Model):
    """
    Modèle pour les commentaires sur les projets
    """

    # Relations
    projet = models.ForeignKey(
        "projects.Projet",
        on_delete=models.CASCADE,
        related_name="commentaires",
        help_text="Projet commenté",
    )

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commentaires_ecrits",
        help_text="Utilisateur qui a écrit le commentaire",
    )

    commentaire_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reponses",
        help_text="Commentaire parent (pour les réponses)",
    )

    # Contenu
    contenu = models.TextField(max_length=1000, help_text="Contenu du commentaire")

    # Modération
    est_signale = models.BooleanField(
        default=False, help_text="Commentaire signalé par d'autres utilisateurs"
    )

    nombre_signalements = models.PositiveIntegerField(
        default=0, help_text="Nombre total de signalements"
    )

    est_masque = models.BooleanField(
        default=False, help_text="Commentaire masqué par un modérateur"
    )

    raison_masquage = models.CharField(
        max_length=200, blank=True, null=True, help_text="Raison du masquage"
    )

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["date_creation"]
        indexes = [
            models.Index(fields=["projet", "date_creation"], name="comment_projet_date_idx"),
            models.Index(fields=["auteur", "-date_creation"], name="comment_auteur_date_idx"),
            models.Index(fields=["est_signale", "est_masque"], name="comment_moderation_idx"),
        ]

    def __str__(self):
        if self.commentaire_parent:
            return f"Réponse de {self.auteur.get_full_name()} à {self.commentaire_parent.auteur.get_full_name()}"
        return f"Commentaire de {self.auteur.get_full_name()} sur {self.projet.titre}"

    @property
    def est_reponse(self):
        """Détermine si c'est une réponse à un autre commentaire"""
        return self.commentaire_parent is not None

    @property
    def est_reponse_porteur(self):
        """Détermine si c'est une réponse du porteur de projet"""
        return self.auteur == self.projet.porteur

    @property
    def peut_repondre(self):
        """Détermine si on peut répondre à ce commentaire (pas de réponse à une réponse)"""
        return self.commentaire_parent is None


class Favori(models.Model):
    """
    Modèle pour les projets mis en favoris par les utilisateurs
    """

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favoris",
        help_text="Utilisateur qui met en favori",
    )

    projet = models.ForeignKey(
        "projects.Projet",
        on_delete=models.CASCADE,
        related_name="mis_en_favoris",
        help_text="Projet mis en favori",
    )

    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ["utilisateur", "projet"]
        ordering = ["-date_ajout"]

    def __str__(self):
        return f"{self.utilisateur.get_full_name()} → {self.projet.titre}"


class Partage(models.Model):
    """
    Modèle pour tracer les partages de projets
    """

    PLATEFORME_CHOICES = [
        ("facebook", "Facebook"),
        ("twitter", "Twitter"),
        ("whatsapp", "WhatsApp"),
        ("linkedin", "LinkedIn"),
        ("email", "Email"),
        ("lien_copie", "Lien copié"),
    ]

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="partages_effectues",
        blank=True,
        null=True,
        help_text="Utilisateur qui partage (peut être anonyme)",
    )

    projet = models.ForeignKey(
        "projects.Projet",
        on_delete=models.CASCADE,
        related_name="partages",
        help_text="Projet partagé",
    )

    plateforme = models.CharField(
        max_length=20, choices=PLATEFORME_CHOICES, help_text="Plateforme de partage"
    )

    date_partage = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Partage"
        verbose_name_plural = "Partages"
        ordering = ["-date_partage"]

    def __str__(self):
        utilisateur = (
            self.utilisateur.get_full_name() if self.utilisateur else "Anonyme"
        )
        return f"{self.projet.titre} partagé sur {self.get_plateforme_display()} par {utilisateur}"  # type: ignore


class Signalement(models.Model):
    """
    Modèle pour les signalements de contenu inapproprié
    """

    TYPE_SIGNALEMENT_CHOICES = [
        ("projet", "Projet"),
        ("commentaire", "Commentaire"),
        ("utilisateur", "Utilisateur"),
    ]

    MOTIF_CHOICES = [
        ("fraude", "Fraude ou escroquerie"),
        ("contenu_inapproprie", "Contenu inapproprié"),
        ("informations_fausses", "Informations fausses"),
        ("spam", "Spam ou contenu commercial non sollicité"),
        ("violation_droits", "Violation de droits d'auteur"),
        ("incitation_haine", "Incitation à la haine"),
        ("autre", "Autre (préciser en description)"),
    ]

    STATUT_CHOICES = [
        ("nouveau", "Nouveau"),
        ("en_cours", "En cours de traitement"),
        ("traite", "Traité"),
        ("rejete", "Rejeté (non fondé)"),
    ]

    auteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="signalements_effectues",
        help_text="Utilisateur qui effectue le signalement",
    )

    type_signalement = models.CharField(
        max_length=20,
        choices=TYPE_SIGNALEMENT_CHOICES,
        help_text="Type d'élément signalé",
    )

    objet_signale_id = models.PositiveIntegerField(
        help_text="ID de l'objet signalé (projet, commentaire, utilisateur)"
    )

    motif = models.CharField(
        max_length=30, choices=MOTIF_CHOICES, help_text="Motif du signalement"
    )

    description = models.TextField(
        max_length=1000, help_text="Description détaillée du signalement"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="nouveau",
        help_text="Statut du traitement",
    )

    decision_admin = models.TextField(
        blank=True, null=True, help_text="Décision et commentaires de l'administrateur"
    )

    date_signalement = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(
        blank=True, null=True, help_text="Date de traitement par un admin"
    )

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ["-date_signalement"]
        # Un utilisateur ne peut signaler le même objet qu'une fois
        unique_together = ["auteur", "type_signalement", "objet_signale_id"]
        indexes = [
            models.Index(fields=["statut", "-date_signalement"], name="signal_statut_date_idx"),
            models.Index(fields=["type_signalement", "objet_signale_id"], name="signal_type_obj_idx"),
        ]

    def __str__(self):
        return f"Signalement {self.get_motif_display()} par {self.auteur.get_full_name()}"  # type: ignore
