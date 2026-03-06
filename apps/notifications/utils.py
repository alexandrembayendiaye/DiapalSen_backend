from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def creer_notification(
    destinataire,
    type_notification,
    titre,
    contenu,
    lien_action=None,
    donnees_contextuelles=None,
):
    """
    Fonction utilitaire pour créer une notification
    """
    return Notification.objects.create(
        destinataire=destinataire,
        type_notification=type_notification,
        titre=titre,
        contenu=contenu,
        lien_action=lien_action or "",
        donnees_contextuelles=donnees_contextuelles or {},
    )


# Fonctions spécifiques par type de notification


def notifier_projet_valide(projet, commentaire_admin=""):
    """Notifie le porteur que son projet est validé"""
    contenu = f"Félicitations ! Votre projet a été approuvé avec le type de financement '{projet.get_type_financement_display()}'. Votre campagne est maintenant active."
    if commentaire_admin:
        contenu += f"\n\nMessage de l'administrateur :\n{commentaire_admin}"

    creer_notification(
        destinataire=projet.porteur,
        type_notification="projet_valide",
        titre=f"🎉 Votre projet '{projet.titre}' a été validé !",
        contenu=contenu,
        lien_action=f"/projets/{projet.id}",
        donnees_contextuelles={
            "projet_id": projet.id,
            "type_financement": projet.type_financement,
            "montant_objectif": float(projet.montant_objectif),
            "commentaire_admin": commentaire_admin,
        },
    )


def notifier_projet_rejete(projet, motif):
    """Notifie le porteur que son projet est rejeté définitivement"""
    creer_notification(
        destinataire=projet.porteur,
        type_notification="projet_rejete",
        titre=f"❌ Votre projet '{projet.titre}' n'a pas été validé",
        contenu=f"Votre projet n'a malheureusement pas pu être validé.\n\nMotif du rejet :\n{motif}",
        lien_action=f"/mes-projets/{projet.id}/commentaires",
        donnees_contextuelles={"projet_id": projet.id, "motif_rejet": motif},
    )


def notifier_modification_demandee(projet, commentaire_admin):
    """Notifie le porteur qu'une modification est demandée sur son projet"""
    creer_notification(
        destinataire=projet.porteur,
        type_notification="infos_demandees",
        titre=f"✏️ Modification demandée sur '{projet.titre}'",
        contenu=f"L'administrateur a demandé des modifications sur votre projet avant de pouvoir le valider.\n\nDemande de l'administrateur :\n{commentaire_admin}\n\nVeuillez modifier votre projet et le soumettre à nouveau.",
        lien_action=f"/mes-projets/{projet.id}/commentaires",
        donnees_contextuelles={
            "projet_id": projet.id,
            "commentaire_admin": commentaire_admin,
            "action_requise": True,
        },
    )


def notifier_nouvelle_contribution(contribution):
    """Notifie le porteur d'une nouvelle contribution"""
    creer_notification(
        destinataire=contribution.projet.porteur,
        type_notification="nouvelle_contribution",
        titre=f"💰 Nouvelle contribution de {contribution.montant} FCFA !",
        contenu=f"{contribution.contributeur_nom_affiche} a contribué {contribution.montant} FCFA à votre projet '{contribution.projet.titre}'.",
        lien_action=f"/projets/{contribution.projet.id}",
        donnees_contextuelles={
            "contribution_id": contribution.id,
            "montant": float(contribution.montant),
            "contributeur_nom": contribution.contributeur_nom_affiche,
            "projet_id": contribution.projet.id,
        },
    )


def notifier_contribution_confirmee(contribution):
    """Notifie le contributeur que sa contribution est confirmée"""
    creer_notification(
        destinataire=contribution.contributeur,
        type_notification="contribution_confirmee",
        titre=f"✅ Votre contribution de {contribution.montant} FCFA est confirmée",
        contenu=f"Merci ! Votre contribution au projet '{contribution.projet.titre}' a été traitée avec succès. Référence : {contribution.reference_paiement}",
        lien_action=f"/mes-contributions",
        donnees_contextuelles={
            "contribution_id": contribution.id,
            "montant": float(contribution.montant),
            "projet_titre": contribution.projet.titre,
            "reference": contribution.reference_paiement,
        },
    )


def notifier_nouveau_commentaire(commentaire):
    """Notifie le porteur d'un nouveau commentaire"""
    creer_notification(
        destinataire=commentaire.projet.porteur,
        type_notification="commentaire_projet",
        titre=f"💬 Nouveau commentaire sur votre projet",
        contenu=f"{commentaire.auteur.get_full_name()} a commenté votre projet '{commentaire.projet.titre}' : \"{commentaire.contenu[:100]}{'...' if len(commentaire.contenu) > 100 else ''}\"",
        lien_action=f"/projets/{commentaire.projet.id}#commentaire-{commentaire.id}",
        donnees_contextuelles={
            "commentaire_id": commentaire.id,
            "auteur_nom": commentaire.auteur.get_full_name(),
            "projet_id": commentaire.projet.id,
        },
    )


def notifier_objectif_atteint(projet):
    """Notifie le porteur que l'objectif est atteint"""
    creer_notification(
        destinataire=projet.porteur,
        type_notification="objectif_atteint",
        titre=f"🎯 Objectif atteint pour '{projet.titre}' !",
        contenu=f"Félicitations ! Votre projet a atteint son objectif de {projet.montant_objectif} FCFA. Vous avez collecté {projet.montant_collecte} FCFA grâce à {projet.nombre_contributeurs} contributeurs.",
        lien_action=f"/projets/{projet.id}",
        donnees_contextuelles={
            "projet_id": projet.id,
            "montant_collecte": float(projet.montant_collecte),
            "pourcentage": projet.pourcentage_atteint,
        },
    )


def notifier_bienvenue(utilisateur):
    """Notification de bienvenue pour nouveaux utilisateurs"""
    creer_notification(
        destinataire=utilisateur,
        type_notification="bienvenue",
        titre=f"🌟 Bienvenue sur DiapalSen, {utilisateur.first_name} !",
        contenu="Merci de rejoindre notre plateforme de crowdfunding sénégalaise ! Découvrez les projets en cours ou créez le vôtre pour obtenir du financement.",
        lien_action="/projets",
        donnees_contextuelles={"type_utilisateur": utilisateur.type_utilisateur},
    )


def notifier_projet_soumis_admin(projet):
    """Notifie les admins qu'un nouveau projet est soumis pour validation"""
    # Récupérer tous les admins (superusers)
    admins = User.objects.filter(is_superuser=True)

    for admin in admins:
        creer_notification(
            destinataire=admin,
            type_notification="projet_soumis",
            titre=f"📋 Nouveau projet à valider: '{projet.titre}'",
            contenu=f"Le porteur {projet.porteur.get_full_name()} a soumis le projet '{projet.titre}' pour validation. Objectif: {projet.montant_objectif} FCFA.",
            lien_action=f"/admin/projets/{projet.id}/detail",
            donnees_contextuelles={
                "projet_id": projet.id,
                "porteur_id": projet.porteur.id,
                "porteur_nom": projet.porteur.get_full_name(),
                "montant_objectif": float(projet.montant_objectif),
            },
        )
