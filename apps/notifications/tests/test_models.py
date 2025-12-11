"""
Tests unitaires pour le modèle Notification
"""
import pytest
from apps.notifications.models import Notification


@pytest.mark.unit
class TestNotificationModel:
    """Tests du modèle Notification"""

    def test_create_notification(self, db, user_contributeur):
        """Test création d'une notification"""
        notif = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="contribution_confirmee",
            titre="Contribution confirmée !",
            contenu="Votre contribution a été validée",
            lien_action="/projets/1"
        )
        
        assert notif.destinataire == user_contributeur
        assert notif.est_lue is False
        assert notif.date_lecture is None

    def test_marquer_comme_lue(self, db, user_contributeur):
        """Test méthode marquer_comme_lue()"""
        notif = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="bienvenue",
            titre="Bienvenue !",
            contenu="Bienvenue sur DiapalSen"
        )
        
        assert notif.est_lue is False
        
        notif.marquer_comme_lue()
        
        assert notif.est_lue is True
        assert notif.date_lecture is not None

    def test_marquer_comme_lue_deja_lue(self, db, user_contributeur):
        """Test marquer_comme_lue() sur notification déjà lue"""
        notif = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="bienvenue",
            titre="Test",
            contenu="Test"
        )
        
        notif.marquer_comme_lue()
        premiere_date = notif.date_lecture
        
        # Marquer à nouveau comme lue
        notif.marquer_comme_lue()
        
        # La date ne devrait pas changer
        assert notif.date_lecture == premiere_date

    def test_notification_str_representation(self, db, user_contributeur):
        """Test représentation string de la notification"""
        notif = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="bienvenue",
            titre="Bienvenue sur DiapalSen",
            contenu="Test"
        )
        
        expected = "Jean Dupont - Bienvenue sur DiapalSen"
        assert str(notif) == expected

    def test_notification_str_representation_lue(self, db, user_contributeur):
        """Test représentation string pour notification lue"""
        notif = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="bienvenue",
            titre="Test",
            contenu="Test"
        )
        notif.marquer_comme_lue()
        
        assert " ✓" in str(notif)

    def test_notification_ordering(self, db, user_contributeur):
        """Test ordre des notifications (plus récentes en premier)"""
        notif1 = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="bienvenue",
            titre="Première",
            contenu="Test"
        )
        notif2 = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="bienvenue",
            titre="Deuxième",
            contenu="Test"
        )
        
        notifications = list(Notification.objects.all())
        assert notifications[0] == notif2  # Plus récente en premier

    def test_notification_donnees_contextuelles(self, db, user_contributeur):
        """Test stockage de données contextuelles JSON"""
        notif = Notification.objects.create(
            destinataire=user_contributeur,
            type_notification="nouvelle_contribution",
            titre="Nouvelle contribution",
            contenu="Test",
            donnees_contextuelles={
                "contribution_id": 123,
                "montant": "5000",
                "projet_id": 456
            }
        )
        
        assert notif.donnees_contextuelles["contribution_id"] == 123
        assert notif.donnees_contextuelles["montant"] == "5000"
        assert notif.donnees_contextuelles["projet_id"] == 456
