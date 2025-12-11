"""
Tests unitaires pour les modèles de l'app interactions
"""
import pytest
from apps.interactions.models import Commentaire, Favori, Partage, Signalement


@pytest.mark.unit
class TestCommentaireModel:
    """Tests du modèle Commentaire"""

    def test_create_commentaire(self, db, projet_actif, user_contributeur):
        """Test création d'un commentaire"""
        commentaire = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_contributeur,
            contenu="Excellent projet, je soutiens !"
        )
        
        assert commentaire.projet == projet_actif
        assert commentaire.auteur == user_contributeur
        assert commentaire.est_signale is False
        assert commentaire.est_masque is False

    def test_commentaire_reponse(self, db, projet_actif, user_contributeur, user_porteur):
        """Test création d'une réponse à un commentaire"""
        commentaire_parent = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_contributeur,
            contenu="Question sur le projet"
        )
        
        reponse = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_porteur,
            commentaire_parent=commentaire_parent,
            contenu="Réponse du porteur"
        )
        
        assert reponse.est_reponse is True
        assert reponse.commentaire_parent == commentaire_parent

    def test_est_reponse_porteur(self, db, projet_actif, user_porteur):
        """Test property est_reponse_porteur"""
        commentaire = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_porteur,
            contenu="Mise à jour du porteur"
        )
        
        assert commentaire.est_reponse_porteur is True

    def test_peut_repondre(self, db, projet_actif, user_contributeur, user_porteur):
        """Test property peut_repondre"""
        # Commentaire principal peut recevoir des réponses
        commentaire = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_contributeur,
            contenu="Commentaire principal"
        )
        assert commentaire.peut_repondre is True
        
        # Réponse ne peut pas recevoir de réponse
        reponse = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_porteur,
            commentaire_parent=commentaire,
            contenu="Réponse"
        )
        assert reponse.peut_repondre is False

    def test_commentaire_str_representation(self, db, projet_actif, user_contributeur):
        """Test représentation string du commentaire"""
        commentaire = Commentaire.objects.create(
            projet=projet_actif,
            auteur=user_contributeur,
            contenu="Test"
        )
        
        expected = f"Commentaire de Jean Dupont sur {projet_actif.titre}"
        assert str(commentaire) == expected


@pytest.mark.unit
class TestFavoriModel:
    """Tests du modèle Favori"""

    def test_create_favori(self, db, projet_actif, user_contributeur):
        """Test création d'un favori"""
        favori = Favori.objects.create(
            utilisateur=user_contributeur,
            projet=projet_actif
        )
        
        assert favori.utilisateur == user_contributeur
        assert favori.projet == projet_actif

    def test_favori_unique_together(self, db, projet_actif, user_contributeur):
        """Test contrainte d'unicité (un user ne peut favoriser qu'une fois)"""
        Favori.objects.create(
            utilisateur=user_contributeur,
            projet=projet_actif
        )
        
        # Tentative de créer un doublon
        with pytest.raises(Exception):  # IntegrityError
            Favori.objects.create(
                utilisateur=user_contributeur,
                projet=projet_actif
            )

    def test_favori_str_representation(self, db, projet_actif, user_contributeur):
        """Test représentation string du favori"""
        favori = Favori.objects.create(
            utilisateur=user_contributeur,
            projet=projet_actif
        )
        
        expected = f"Jean Dupont → {projet_actif.titre}"
        assert str(favori) == expected


@pytest.mark.unit
class TestPartageModel:
    """Tests du modèle Partage"""

    def test_create_partage_authenticated(self, db, projet_actif, user_contributeur):
        """Test création d'un partage par utilisateur authentifié"""
        partage = Partage.objects.create(
            utilisateur=user_contributeur,
            projet=projet_actif,
            plateforme="facebook"
        )
        
        assert partage.utilisateur == user_contributeur
        assert partage.plateforme == "facebook"

    def test_create_partage_anonyme(self, db, projet_actif):
        """Test création d'un partage anonyme"""
        partage = Partage.objects.create(
            projet=projet_actif,
            plateforme="whatsapp"
        )
        
        assert partage.utilisateur is None
        assert partage.plateforme == "whatsapp"

    def test_partage_str_representation(self, db, projet_actif, user_contributeur):
        """Test représentation string du partage"""
        partage = Partage.objects.create(
            utilisateur=user_contributeur,
            projet=projet_actif,
            plateforme="twitter"
        )
        
        assert "Twitter" in str(partage)
        assert "Jean Dupont" in str(partage)


@pytest.mark.unit
class TestSignalementModel:
    """Tests du modèle Signalement"""

    def test_create_signalement(self, db, projet_actif, user_contributeur):
        """Test création d'un signalement"""
        signalement = Signalement.objects.create(
            auteur=user_contributeur,
            type_signalement="projet",
            objet_signale_id=projet_actif.id,
            motif="fraude",
            description="Ce projet semble frauduleux"
        )
        
        assert signalement.auteur == user_contributeur
        assert signalement.statut == "nouveau"
        assert signalement.motif == "fraude"

    def test_signalement_unique_together(self, db, projet_actif, user_contributeur):
        """Test qu'un user ne peut signaler le même objet qu'une fois"""
        Signalement.objects.create(
            auteur=user_contributeur,
            type_signalement="projet",
            objet_signale_id=projet_actif.id,
            motif="fraude",
            description="Test"
        )
        
        # Tentative de signaler à nouveau
        with pytest.raises(Exception):  # IntegrityError
            Signalement.objects.create(
                auteur=user_contributeur,
                type_signalement="projet",
                objet_signale_id=projet_actif.id,
                motif="spam",
                description="Test 2"
            )

    def test_signalement_str_representation(self, db, projet_actif, user_contributeur):
        """Test représentation string du signalement"""
        signalement = Signalement.objects.create(
            auteur=user_contributeur,
            type_signalement="projet",
            objet_signale_id=projet_actif.id,
            motif="contenu_inapproprie",
            description="Test"
        )
        
        assert "Jean Dupont" in str(signalement)
