"""
Package settings pour DiapalSen

Charge automatiquement les settings appropriés selon l'environnement.
Sur Heroku, DJANGO_SETTINGS_MODULE est défini, donc ce fichier ne sera pas utilisé.
En local, il charge development par défaut.
"""
import os

# Vérifie si on est sur Heroku (production)
# En production, Heroku définit DJANGO_SETTINGS_MODULE directement
# Ce fichier n'est utilisé qu'en développement local
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
else:
    # En développement local uniquement
    try:
        from .development import *
    except Exception as e:
        print(f"⚠️ Erreur chargement development.py: {e}")
        # Fallback sur production si development échoue
        from .production import *

print(f"🌍 Environnement Django: {environment}")