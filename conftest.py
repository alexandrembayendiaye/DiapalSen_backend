"""
Configuration globale pytest pour DiapalSen
Fixtures partagées entre tous les tests
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.projects.models import Projet, Categorie
from apps.contributions.models import Contribution

User = get_user_model()


# ========== FIXTURES UTILISATEURS ==========

@pytest.fixture
def user_contributeur(db):
    """Crée un utilisateur contributeur de test"""
    return User.objects.create_user(
        username="contributeur_test",
        email="contributeur@test.com",
        password="testpass123",
        first_name="Jean",
        last_name="Dupont",
        type_utilisateur="contributeur",
        telephone="+221771234567",
        region="dakar",
        statut_compte="actif"
    )


@pytest.fixture
def user_porteur(db):
    """Crée un utilisateur porteur de projet de test"""
    return User.objects.create_user(
        username="porteur_test",
        email="porteur@test.com",
        password="testpass123",
        first_name="Marie",
        last_name="Martin",
        type_utilisateur="porteur",
        telephone="+221772345678",
        region="thies",
        statut_compte="actif"
    )


@pytest.fixture
def user_admin(db):
    """Crée un utilisateur administrateur de test"""
    return User.objects.create_superuser(
        username="admin_test",
        email="admin@test.com",
        password="testpass123",
        first_name="Admin",
        last_name="DiapalSen",
        type_utilisateur="admin"
    )


# ========== FIXTURES PROJETS ==========

@pytest.fixture
def categorie(db):
    """Crée une catégorie de test"""
    return Categorie.objects.create(
        nom="Agriculture & Élevage",
        description="Projets agricoles et d'élevage",
        icone="🌾",
        ordre_affichage=1,
        est_active=True
    )


@pytest.fixture
def projet_brouillon(db, user_porteur, categorie):
    """Crée un projet en brouillon"""
    return Projet.objects.create(
        porteur=user_porteur,
        categorie=categorie,
        titre="Projet Test Brouillon",
        description_courte="Description courte du projet test",
        description_complete="Description complète et détaillée du projet test",
        region="dakar",
        ville="Dakar",
        montant_objectif=Decimal("500000"),
        duree_campagne_jours=30,
        statut="brouillon"
    )


@pytest.fixture
def projet_actif(db, user_porteur, categorie):
    """Crée un projet actif (campagne en cours)"""
    from django.utils import timezone
    from datetime import timedelta
    
    projet = Projet.objects.create(
        porteur=user_porteur,
        categorie=categorie,
        titre="Projet Test Actif",
        description_courte="Projet en campagne active",
        description_complete="Description complète du projet actif",
        region="thies",
        ville="Thiès",
        montant_objectif=Decimal("1000000"),
        duree_campagne_jours=60,
        statut="actif",
        type_financement="tout_ou_rien",
        date_debut_campagne=timezone.now(),
        date_fin_campagne=timezone.now() + timedelta(days=60)
    )
    return projet


# ========== FIXTURES CONTRIBUTIONS ==========

@pytest.fixture
def contribution_validee(db, projet_actif, user_contributeur):
    """Crée une contribution validée"""
    return Contribution.objects.create(
        projet=projet_actif,
        contributeur=user_contributeur,
        montant=Decimal("5000"),
        moyen_paiement="wave",
        statut_paiement="valide",
        message_soutien="Bon courage pour votre projet !"
    )


@pytest.fixture
def contribution_en_attente(db, projet_actif, user_contributeur):
    """Crée une contribution en attente"""
    return Contribution.objects.create(
        projet=projet_actif,
        contributeur=user_contributeur,
        montant=Decimal("3000"),
        moyen_paiement="orange_money",
        statut_paiement="en_attente"
    )


# ========== FIXTURES API ==========

@pytest.fixture
def api_client():
    """Client API REST Framework"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user_contributeur):
    """Client API authentifié avec un contributeur"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user_contributeur)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, user_admin):
    """Client API authentifié avec un admin"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user_admin)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
