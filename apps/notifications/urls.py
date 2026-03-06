from django.urls import path
from . import views

urlpatterns = [
    # Notifications
    path("", views.MesNotificationsListView.as_view(), name="mes-notifications"),
    path("non-lues/", views.notifications_non_lues_view, name="notifications-non-lues"),
    path(
        "<int:notification_id>/lire/",
        views.marquer_notification_lue_view,
        name="marquer-notification-lue",
    ),
    path(
        "marquer-toutes-lues/",
        views.marquer_toutes_lues_view,
        name="marquer-toutes-lues",
    ),
    path(
        "<int:notification_id>/supprimer/",
        views.supprimer_notification_view,
        name="supprimer-notification",
    ),
]
