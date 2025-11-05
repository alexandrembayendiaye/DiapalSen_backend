from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur
from .forms import UtilisateurCreationForm, UtilisateurChangeForm


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    add_form = UtilisateurCreationForm
    form = UtilisateurChangeForm
    model = Utilisateur
    """
    Interface d'administration personnalisée pour le modèle Utilisateur.
    """

    # ----- Colonnes affichées dans la liste -----
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "type_utilisateur",
        "ville",
        "is_active",
        "is_staff",
    )
    list_filter = ("type_utilisateur", "is_active", "is_staff", "ville")
    search_fields = ("email", "first_name", "last_name", "ville")

    ordering = ("-id",)
    list_per_page = 25

    # ----- Organisation des champs dans le formulaire -----
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informations personnelles",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_de_naissance",
                    "numero_telephone",
                    "adresse",
                    "ville",
                    "photo_profil",
                )
            },
        ),
        (
            "Rôle et permissions",
            {
                "fields": (
                    "type_utilisateur",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )

    # ----- Champs affichés lors de l'ajout d'un nouvel utilisateur -----
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "type_utilisateur",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    # ----- Champs en lecture seule -----
    readonly_fields = ("last_login", "date_joined")
