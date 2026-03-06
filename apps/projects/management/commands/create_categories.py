from django.core.management.base import BaseCommand
from apps.projects.models import Categorie


class Command(BaseCommand):
    help = "Créer les catégories de projets par défaut"

    def handle(self, *args, **options):
        categories = [
            {"nom": "Agriculture & Élevage", "icone": "🌾", "ordre": 1},
            {"nom": "Technologie & Innovation", "icone": "💻", "ordre": 2},
            {"nom": "Éducation & Formation", "icone": "📚", "ordre": 3},
            {"nom": "Santé & Bien-être", "icone": "🏥", "ordre": 4},
            {"nom": "Artisanat & Mode", "icone": "🎨", "ordre": 5},
            {"nom": "Culture & Arts", "icone": "🎭", "ordre": 6},
            {"nom": "Commerce & Services", "icone": "🏪", "ordre": 7},
            {"nom": "Environnement", "icone": "🌍", "ordre": 8},
            {"nom": "Sport & Loisirs", "icone": "⚽", "ordre": 9},
            {"nom": "Social & Communautaire", "icone": "🤝", "ordre": 10},
            {"nom": "Tourisme", "icone": "✈️", "ordre": 11},
            {"nom": "Autre", "icone": "📦", "ordre": 12},
        ]

        created_count = 0
        for cat_data in categories:
            categorie, created = Categorie.objects.get_or_create(
                nom=cat_data["nom"],
                defaults={
                    "icone": cat_data["icone"],
                    "ordre_affichage": cat_data["ordre"],
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Catégorie créée: {categorie}")

        self.stdout.write(
            self.style.SUCCESS(f"✅ {created_count} catégories créées avec succès!")
        )
