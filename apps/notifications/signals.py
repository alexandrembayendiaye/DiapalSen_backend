from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.projects.models import Projet, ValidationProjet
from apps.contributions.models import Contribution
from apps.interactions.models import Commentaire
from django.contrib.auth import get_user_model
from .utils import (
    notifier_projet_valide,
    notifier_projet_rejete,
    notifier_modification_demandee,
    notifier_nouvelle_contribution,
    notifier_contribution_confirmee,
    notifier_nouveau_commentaire,
    notifier_objectif_atteint,
    notifier_bienvenue,
)

User = get_user_model()


@receiver(post_save, sender=User)
def notification_bienvenue(sender, instance, created, **kwargs):
    """Envoie une notification de bienvenue aux nouveaux utilisateurs"""
    if created:
        notifier_bienvenue(instance)


@receiver(post_save, sender=ValidationProjet)
def notification_validation_projet(sender, instance, created, **kwargs):
    """Envoie des notifications lors de la validation/rejet/demande de modification d'un projet"""
    if created:
        if instance.decision == "approuve":
            notifier_projet_valide(instance.projet, instance.commentaire)
        elif instance.decision == "rejete":
            notifier_projet_rejete(instance.projet, instance.motif_rejet or instance.commentaire)
        elif instance.decision == "infos_demandees":
            notifier_modification_demandee(instance.projet, instance.commentaire)


@receiver(post_save, sender=Contribution)
def notification_contribution(sender, instance, created, **kwargs):
    """Envoie des notifications lors d'une nouvelle contribution"""
    if created and instance.statut_paiement == "valide":
        # Notifier le porteur de la nouvelle contribution
        notifier_nouvelle_contribution(instance)

        # Notifier le contributeur de la confirmation
        notifier_contribution_confirmee(instance)

        # Vérifier si l'objectif est atteint pour la première fois
        projet = instance.projet
        if (
            projet.est_finance
            and projet.contributions.filter(statut_paiement="valide").count() == 1
        ):
            # C'est la première fois que l'objectif est atteint
            notifier_objectif_atteint(projet)


@receiver(post_save, sender=Commentaire)
def notification_commentaire(sender, instance, created, **kwargs):
    """Envoie une notification au porteur lors d'un nouveau commentaire"""
    if created and not instance.est_masque:
        # Ne pas notifier si c'est le porteur qui commente son propre projet
        if instance.auteur != instance.projet.porteur:
            notifier_nouveau_commentaire(instance)
