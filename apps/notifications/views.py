from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer, NotificationUpdateSerializer


class MesNotificationsListView(generics.ListAPIView):
    """
    API pour lister mes notifications
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user).order_by(
            "-date_creation"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notifications_non_lues_view(request):
    """
    API pour récupérer le nombre de notifications non lues
    """
    count = Notification.objects.filter(
        destinataire=request.user, est_lue=False
    ).count()

    return Response({"count": count, "has_unread": count > 0})


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def marquer_notification_lue_view(request, notification_id):
    """
    API pour marquer une notification comme lue
    """
    notification = get_object_or_404(
        Notification, id=notification_id, destinataire=request.user
    )

    notification.marquer_comme_lue()

    return Response(
        {
            "message": "Notification marquée comme lue",
            "notification": NotificationSerializer(notification).data,
        }
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def marquer_toutes_lues_view(request):
    """
    API pour marquer toutes les notifications comme lues
    """
    notifications_non_lues = Notification.objects.filter(
        destinataire=request.user, est_lue=False
    )

    count = notifications_non_lues.count()

    # Marquer toutes comme lues
    from django.utils import timezone

    notifications_non_lues.update(est_lue=True, date_lecture=timezone.now())

    return Response(
        {"message": f"{count} notifications marquées comme lues", "count": count}
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def supprimer_notification_view(request, notification_id):
    """
    API pour supprimer une notification
    """
    notification = get_object_or_404(
        Notification, id=notification_id, destinataire=request.user
    )

    notification.delete()

    return Response(
        {"message": "Notification supprimée"}, status=status.HTTP_204_NO_CONTENT
    )
