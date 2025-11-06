from django.db import models


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
