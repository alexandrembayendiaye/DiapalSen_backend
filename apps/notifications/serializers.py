from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications utilisateur"""

    type_notification_display = serializers.CharField(
        source="get_type_notification_display", read_only=True
    )
    temps_ecoule = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "type_notification",
            "type_notification_display",
            "titre",
            "contenu",
            "lien_action",
            "est_lue",
            "date_creation",
            "date_lecture",
            "temps_ecoule",
            "donnees_contextuelles",
        ]
        read_only_fields = ["id", "date_creation", "date_lecture"]

    def get_temps_ecoule(self, obj):
        """Calcule le temps écoulé depuis la création"""
        from django.utils import timezone
        from datetime import datetime

        now = timezone.now()
        delta = now - obj.date_creation

        if delta.days > 0:
            return f"il y a {delta.days} jour{'s' if delta.days > 1 else ''}"
        elif delta.seconds > 3600:
            heures = delta.seconds // 3600
            return f"il y a {heures} heure{'s' if heures > 1 else ''}"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "à l'instant"


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour marquer une notification comme lue"""

    class Meta:
        model = Notification
        fields = ["est_lue"]
