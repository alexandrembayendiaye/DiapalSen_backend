from django.contrib import admin
from .models import Categorie, Project


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "est_active", "ordre_affichage")
    list_filter = ("est_active",)
    search_fields = ("nom",)
    ordering = ("ordre_affichage",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "porteur",
        "categorie",
        "statut",
        "montant_objectif",
        "montant_actuel",
    )
    list_filter = ("statut", "categorie")
    search_fields = ("titre", "description", "porteur__email")
    ordering = ("-date_creation",)
