"""
Tests unitaires pour le modèle Contribution
"""
import pytest
from decimal import Decimal
from apps.contributions.models import Contribution


@pytest.mark.unit
class TestContributionModel:
    """Tests du modèle Contribution"""

    def test_create_contribution(self, contribution_en_attente):
        """Test création d'une contribution"""
        assert contribution_en_attente.montant == Decimal("3000")
        assert contribution_en_attente.moyen_paiement == "orange_money"
        assert contribution_en_attente.statut_paiement == "en_attente"

    def test_reference_paiement_auto_generated(self, db, projet_actif, user_contributeur):
        """Test génération automatique de la référence de paiement"""
        contrib = Contribution.objects.create(
            projet=projet_actif,
            contributeur=user_contributeur,
            montant=Decimal("2000"),
            moyen_paiement="wave"
        )
        
        assert contrib.reference_paiement is not None
        assert contrib.reference_paiement.startswith("DPS_")
        assert len(contrib.reference_paiement) == 16  # DPS_ + 12 caractères

    def test_reference_paiement_unique(self, db, projet_actif, user_contributeur):
        """Test unicité de la référence de paiement"""
        contrib1 = Contribution.objects.create(
            projet=projet_actif,
            contributeur=user_contributeur,
            montant=Decimal("1000"),
            moyen_paiement="wave"
        )
        contrib2 = Contribution.objects.create(
            projet=projet_actif,
            contributeur=user_contributeur,
            montant=Decimal("1000"),
            moyen_paiement="wave"
        )
        
        assert contrib1.reference_paiement != contrib2.reference_paiement

    def test_contributeur_nom_affiche_public(self, contribution_validee):
        """Test nom affiché pour contribution publique"""
        contribution_validee.est_anonyme = False
        contribution_validee.save()
        
        assert contribution_validee.contributeur_nom_affiche == "Jean Dupont"

    def test_contributeur_nom_affiche_anonyme(self, contribution_validee):
        """Test nom affiché pour contribution anonyme"""
        contribution_validee.est_anonyme = True
        contribution_validee.save()
        
        assert contribution_validee.contributeur_nom_affiche == "Contributeur anonyme"

    def test_contribution_str_representation(self, contribution_validee):
        """Test représentation string de la contribution"""
        expected = "5000 FCFA pour Projet Test Actif par Jean Dupont"
        assert str(contribution_validee) == expected

    def test_contribution_str_representation_anonyme(self, contribution_validee):
        """Test représentation string pour contribution anonyme"""
        contribution_validee.est_anonyme = True
        contribution_validee.save()
        
        expected = "5000 FCFA pour Projet Test Actif par Jean Dupont (anonyme)"
        assert str(contribution_validee) == expected

    def test_montant_minimum_validation(self, db, projet_actif, user_contributeur):
        """Test validation du montant minimum (1000 FCFA)"""
        with pytest.raises(Exception):  # ValidationError
            contrib = Contribution.objects.create(
                projet=projet_actif,
                contributeur=user_contributeur,
                montant=Decimal("500"),  # < 1000 FCFA
                moyen_paiement="wave"
            )
            contrib.full_clean()

    def test_contribution_ordering(self, db, projet_actif, user_contributeur):
        """Test ordre des contributions (plus récentes en premier)"""
        contrib1 = Contribution.objects.create(
            projet=projet_actif,
            contributeur=user_contributeur,
            montant=Decimal("1000"),
            moyen_paiement="wave"
        )
        contrib2 = Contribution.objects.create(
            projet=projet_actif,
            contributeur=user_contributeur,
            montant=Decimal("2000"),
            moyen_paiement="wave"
        )
        
        contributions = list(Contribution.objects.all())
        assert contributions[0] == contrib2  # Plus récente en premier

    def test_generer_recu_not_valide(self, contribution_en_attente):
        """Test que generer_recu() ne génère pas de PDF si statut != valide"""
        result = contribution_en_attente.generer_recu()
        assert result is False
        assert not contribution_en_attente.recu_pdf

    def test_generer_recu_already_exists(self, contribution_validee):
        """Test que generer_recu() ne régénère pas si PDF existe déjà"""
        # Simuler qu'un PDF existe déjà
        contribution_validee.recu_pdf = "recus/existing.pdf"
        contribution_validee.save()
        
        result = contribution_validee.generer_recu()
        assert result is False
