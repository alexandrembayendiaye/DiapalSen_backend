from django.apps import AppConfig


class ContributionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contributions"

    def ready(self):
        """Importer les signaux au démarrage de l'application"""
        import apps.contributions.signals  # noqa

