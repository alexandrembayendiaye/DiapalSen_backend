from rest_framework import serializers
<<<<<<< HEAD
from django.contrib.auth import get_user_model

Utilisateur = get_user_model()


# ============================================================
# 1️⃣ Serializer d'inscription
# ============================================================
class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "date_de_naissance",
            "numero_telephone",
            "adresse",
            "ville",
            "type_utilisateur",
            "photo_profil",
        ]

    def create(self, validated_data):
        """
        Crée un utilisateur à partir des données validées.
        """
        password = validated_data.pop("password")
        user = Utilisateur(**validated_data)
=======
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="Minimum 8 caractères, 1 majuscule, 1 chiffre",
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "telephone",
            "type_utilisateur",
            "region",
            "ville",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_email(self, value):
        """Vérifier l'unicité de l'email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value

    def validate(self, attrs):
        """Validation personnalisée"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
>>>>>>> ancienne_version
        user.set_password(password)
        user.save()
        return user


<<<<<<< HEAD
# ============================================================
# 2️⃣ Serializer de profil utilisateur
# ============================================================
class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "date_de_naissance",
            "numero_telephone",
            "adresse",
            "ville",
            "type_utilisateur",
            "photo_profil",
        ]
=======
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur (lecture/modification)"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "telephone",
            "type_utilisateur",
            "photo_profil",
            "biographie",
            "region",
            "ville",
            "date_joined",
            "date_derniere_connexion",
            "statut_compte",
            # ✅ AJOUTEZ CES DEUX LIGNES :
            "is_superuser",
            "is_staff",
        )
        read_only_fields = (
            "id",
            "email",
            "date_joined",
            "statut_compte",
            "is_superuser",
            "is_staff",
        )


class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Valider les identifiants de connexion"""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # CORRECTION : Chercher l'utilisateur par email d'abord
            try:
                user = User.objects.get(email=email)
                # Puis vérifier le mot de passe
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError("Compte désactivé.")
                    attrs["user"] = user
                    return attrs
                else:
                    raise serializers.ValidationError("Identifiants invalides.")
            except User.DoesNotExist:
                raise serializers.ValidationError("Identifiants invalides.")
        else:
            raise serializers.ValidationError("Email et mot de passe requis.")
>>>>>>> ancienne_version
