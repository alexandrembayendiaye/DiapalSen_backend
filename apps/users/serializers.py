from rest_framework import serializers
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
        user.set_password(password)
        user.save()
        return user


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
