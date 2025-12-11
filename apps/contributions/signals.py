"""
Signaux Django pour l'application contributions
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contribution


@receiver(post_save, sender=Contribution)
def contribution_validee_signal(sender, instance, created, **kwargs):
    """
    Signal déclenché après sauvegarde d'une contribution
    Génère automatiquement le reçu PDF et envoie l'email si le paiement est validé
    """
    # Vérifier si le statut vient de passer à "valide"
    if instance.statut_paiement == "valide" and not instance.recu_pdf:
        # Générer le reçu PDF
        if instance.generer_recu():
            print(f"✅ Reçu PDF généré pour {instance.reference_paiement}")

            # Envoyer l'email avec le reçu
            if instance.envoyer_recu_email():
                print(f"✅ Email envoyé à {instance.contributeur.email}")

            # Créer une notification pour le contributeur
            from apps.notifications.models import Notification

            Notification.objects.create(
                destinataire=instance.contributeur,
                type_notification="contribution_confirmee",
                titre="Contribution confirmée !",
                contenu=f"Votre contribution de {int(instance.montant):,} FCFA au projet '{instance.projet.titre}' a été validée. Vous avez reçu votre reçu par email.".replace(
                    ",", " "
                ),
                lien_action=f"/projets/{instance.projet.id}",
                donnees_contextuelles={
                    "contribution_id": instance.id,
                    "montant": str(instance.montant),
                    "projet_id": instance.projet.id,
                },
            )

            # Créer une notification pour le porteur de projet
            Notification.objects.create(
                destinataire=instance.projet.porteur,
                type_notification="nouvelle_contribution",
                titre="Nouvelle contribution reçue !",
                contenu=f"{instance.contributeur_nom_affiche} a contribué {int(instance.montant):,} FCFA à votre projet '{instance.projet.titre}'.".replace(
                    ",", " "
                ),
                lien_action=f"/mes-projets/{instance.projet.id}",
                donnees_contextuelles={
                    "contribution_id": instance.id,
                    "montant": str(instance.montant),
                    "contributeur": instance.contributeur_nom_affiche,
                },
            )

            # Mettre à jour les statistiques du projet
            projet = instance.projet
            projet.montant_collecte += instance.montant
            projet.nombre_contributeurs = projet.contributions.filter(
                statut_paiement="valide"
            ).values("contributeur").distinct().count()
            projet.save(update_fields=["montant_collecte", "nombre_contributeurs"])

            print(f"✅ Projet mis à jour: {projet.montant_collecte} FCFA collectés")
