"""
Tests unitaires pour le modèle User
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.unit
class TestUserModel:
    """Tests du modèle User personnalisé"""

    def test_create_user_contributeur(self, db):
        """Test création d'un utilisateur contributeur"""
        user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            type_utilisateur="contributeur"
        )
        
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.type_utilisateur == "contributeur"
        assert user.is_contributeur is True
        assert user.is_porteur is False
        assert user.is_admin_custom is False
        assert user.check_password("testpass123")

    def test_create_user_porteur(self, db):
        """Test création d'un utilisateur porteur"""
        user = User.objects.create_user(
            username="porteur",
            email="porteur@example.com",
            password="testpass123",
            type_utilisateur="porteur"
        )
        
        assert user.is_porteur is True
        assert user.is_contributeur is False

    def test_create_superuser(self, db):
        """Test création d'un superuser"""
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        
        assert admin.is_superuser is True
        assert admin.is_staff is True
        assert admin.is_admin_custom is True

    def test_get_full_name(self, user_contributeur):
        """Test méthode get_full_name()"""
        assert user_contributeur.get_full_name() == "Jean Dupont"

    def test_get_full_name_without_names(self, db):
        """Test get_full_name() sans prénom/nom"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        assert user.get_full_name() == "testuser"

    def test_telephone_validation_senegalais(self, db):
        """Test validation du téléphone sénégalais"""
        # Format valide avec +221
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
            telephone="+221771234567"
        )
        assert user1.telephone == "+221771234567"
        
        # Format valide sans +221
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
            telephone="771234567"
        )
        assert user2.telephone == "771234567"

    def test_user_str_representation(self, user_contributeur):
        """Test représentation string du User"""
        expected = "Jean Dupont (contributeur@test.com)"
        assert str(user_contributeur) == expected

    def test_user_ordering(self, db):
        """Test que les users sont ordonnés par date_joined desc"""
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )
        
        users = list(User.objects.all())
        assert users[0] == user2  # Plus récent en premier
        assert users[1] == user1

    def test_user_regions_choices(self, db):
        """Test que toutes les régions du Sénégal sont disponibles"""
        regions = [choice[0] for choice in User.REGION_CHOICES]
        
        assert "dakar" in regions
        assert "thies" in regions
        assert "saint-louis" in regions
        assert "ziguinchor" in regions
        assert len(regions) == 14  # 14 régions du Sénégal

    def test_user_statut_compte_default(self, db):
        """Test que le statut par défaut est 'actif'"""
        user = User.objects.create_user(
            username="test",
            email="test@example.com",
            password="testpass123"
        )
        assert user.statut_compte == "actif"
