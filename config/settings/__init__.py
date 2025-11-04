"""
Package settings pour DiapalSen

Charge automatiquement les settings appropriés selon l'environnement
défini par la variable DJANGO_ENVIRONMENT
"""
import os

# Détermine quel environnement charger
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    from .development import *  # Par défaut

print(f"🌍 Environnement Django: {environment}")