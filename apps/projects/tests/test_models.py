"""
Tests unitaires pour les modèles de l'app projects
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from apps.projects.models import Projet, Categorie, MiseAJourProjet


@pytest.mark.unit
class TestCategorieModel:
    """Tests du modèle Categorie"""

    def test_create_categorie(self, db):
        """Test création d'une catégorie"""
        categorie = Categorie.objects.create(
            nom="Tech & Innovation",
            description="Projets technologiques",
            icone="💻",
            ordre_affichage=1
        )
        
        assert categorie.nom == "Tech & Innovation"
        assert categorie.icone == "💻"
        assert categorie.est_active is True

    def test_categorie_str_with_icon(self, categorie):
        """Test représentation string avec icône"""
        assert str(categorie) == "🌾 Agriculture & Élevage"

    def test_categorie_ordering(self, db):
        """Test ordre d'affichage des catégories"""
        cat1 = Categorie.objects.create(nom="Cat1", ordre_affichage=2)
        cat2 = Categorie.objects.create(nom="Cat2", ordre_affichage=1)
        
        categories = list(Categorie.objects.all())
        assert categories[0] == cat2  # ordre_affichage=1 en premier


@pytest.mark.unit
class TestProjetModel:
    """Tests du modèle Projet"""

    def test_create_projet_brouillon(self, projet_brouillon):
        """Test création d'un projet en brouillon"""
        assert projet_brouillon.titre == "Projet Test Brouillon"
        assert projet_brouillon.statut == "brouillon"
        assert projet_brouillon.montant_collecte == Decimal("0")
        assert projet_brouillon.nombre_contributeurs == 0

    def test_pourcentage_atteint_zero(self, projet_brouillon):
        """Test pourcentage_atteint quand aucune contribution"""
        assert projet_brouillon.pourcentage_atteint == 0

    def test_pourcentage_atteint_partial(self, projet_actif):
        """Test pourcentage_atteint avec contributions partielles"""
        projet_actif.montant_collecte = Decimal("250000")  # 25% de 1M
        projet_actif.save()
        
        assert projet_actif.pourcentage_atteint == 25.0

    def test_pourcentage_atteint_complete(self, projet_actif):
        """Test pourcentage_atteint à 100%"""
        projet_actif.montant_collecte = projet_actif.montant_objectif
        projet_actif.save()
        
        assert projet_actif.pourcentage_atteint == 100.0

    def test_pourcentage_atteint_over(self, projet_actif):
        """Test pourcentage_atteint au-dessus de 100%"""
        projet_actif.montant_collecte = Decimal("1500000")  # 150% de 1M
        projet_actif.save()
        
        assert projet_actif.pourcentage_atteint == 150.0

    def test_est_finance_tout_ou_rien_success(self, projet_actif):
        """Test est_finance pour type 'tout_ou_rien' à 100%"""
        projet_actif.type_financement = "tout_ou_rien"
        projet_actif.montant_collecte = projet_actif.montant_objectif
        projet_actif.save()
        
        assert projet_actif.est_finance is True

    def test_est_finance_tout_ou_rien_fail(self, projet_actif):
        """Test est_finance pour type 'tout_ou_rien' à 99%"""
        projet_actif.type_financement = "tout_ou_rien"
        projet_actif.montant_collecte = Decimal("990000")  # 99%
        projet_actif.save()
        
        assert projet_actif.est_finance is False

    def test_est_finance_flexible_50_success(self, projet_actif):
        """Test est_finance pour type 'flexible_50' à 50%"""
        projet_actif.type_financement = "flexible_50"
        projet_actif.montant_collecte = Decimal("500000")  # 50%
        projet_actif.save()
        
        assert projet_actif.est_finance is True

    def test_est_finance_flexible_50_fail(self, projet_actif):
        """Test est_finance pour type 'flexible_50' à 49%"""
        projet_actif.type_financement = "flexible_50"
        projet_actif.montant_collecte = Decimal("490000")  # 49%
        projet_actif.save()
        
        assert projet_actif.est_finance is False

    def test_est_finance_solidaire(self, projet_actif):
        """Test est_finance pour type 'solidaire' (toujours vrai si > 0)"""
        projet_actif.type_financement = "solidaire"
        projet_actif.montant_collecte = Decimal("1000")  # 0.1%
        projet_actif.save()
        
        assert projet_actif.est_finance is True

    def test_jours_restants_actif(self, projet_actif):
        """Test jours_restants pour projet actif"""
        # Projet actif avec fin dans 60 jours
        jours = projet_actif.jours_restants
        assert 59 <= jours <= 60  # Peut varier légèrement

    def test_jours_restants_termine(self, projet_actif):
        """Test jours_restants pour projet terminé"""
        projet_actif.date_fin_campagne = timezone.now() - timedelta(days=10)
        projet_actif.save()
        
        assert projet_actif.jours_restants == 0

    def test_jours_restants_non_actif(self, projet_brouillon):
        """Test jours_restants pour projet non actif"""
        assert projet_brouillon.jours_restants == 0

    def test_projet_str_representation(self, projet_actif):
        """Test représentation string du Projet"""
        expected = "Projet Test Actif - Campagne active"
        assert str(projet_actif) == expected

    def test_projet_validation_montant_minimum(self, db, user_porteur, categorie):
        """Test validation montant minimum (100k FCFA)"""
        with pytest.raises(Exception):  # ValidationError
            projet = Projet.objects.create(
                porteur=user_porteur,
                categorie=categorie,
                titre="Projet Test",
                description_courte="Test",
                description_complete="Test complet",
                region="dakar",
                ville="Dakar",
                montant_objectif=Decimal("50000"),  # < 100k
                duree_campagne_jours=30
            )
            projet.full_clean()

    def test_projet_validation_montant_maximum(self, db, user_porteur, categorie):
        """Test validation montant maximum (10M FCFA)"""
        with pytest.raises(Exception):  # ValidationError
            projet = Projet.objects.create(
                porteur=user_porteur,
                categorie=categorie,
                titre="Projet Test",
                description_courte="Test",
                description_complete="Test complet",
                region="dakar",
                ville="Dakar",
                montant_objectif=Decimal("15000000"),  # > 10M
                duree_campagne_jours=30
            )
            projet.full_clean()


@pytest.mark.unit
class TestMiseAJourProjetModel:
    """Tests du modèle MiseAJourProjet"""

    def test_peut_voir_public(self, db, projet_actif, user_porteur, user_contributeur):
        """Test peut_voir pour mise à jour publique"""
        maj = MiseAJourProjet.objects.create(
            projet=projet_actif,
            auteur=user_porteur,
            titre="Mise à jour publique",
            contenu="Contenu de la mise à jour",
            visibilite="public"
        )
        
        assert maj.peut_voir(user_contributeur) is True
        assert maj.peut_voir(user_porteur) is True

    def test_peut_voir_contributeurs_only(self, db, projet_actif, user_porteur, 
                                          user_contributeur, contribution_validee):
        """Test peut_voir pour mise à jour réservée aux contributeurs"""
        maj = MiseAJourProjet.objects.create(
            projet=projet_actif,
            auteur=user_porteur,
            titre="Mise à jour contributeurs",
            contenu="Réservé aux contributeurs",
            visibilite="contributeurs"
        )
        
        # Contributeur qui a contribué
        assert maj.peut_voir(user_contributeur) is True
        
        # Utilisateur qui n'a pas contribué
        from django.contrib.auth import get_user_model
        User = get_user_model()
        autre_user = User.objects.create_user(
            username="autre",
            email="autre@test.com",
            password="testpass123"
        )
        assert maj.peut_voir(autre_user) is False
