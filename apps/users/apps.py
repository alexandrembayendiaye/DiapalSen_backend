"""
Configuration de l'application Users pour DiapalSen
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Utilisateurs"

    def ready(self):
        """
        Code à exécuter quand l'application est prête
        Utile pour importer les signaux Django
        """
        pass
