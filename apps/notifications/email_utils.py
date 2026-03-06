from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def envoyer_email_html(destinataire, sujet, template_name, context):
    """
    Fonction utilitaire pour envoyer des emails HTML
    """
    try:
        # Rendu du template HTML
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)  # Version texte

        # En développement, juste logger l'email
        if settings.DEBUG:
            print(f"\n📧 EMAIL SIMULÉ 📧")
            print(f"Destinataire: {destinataire}")
            print(f"Sujet: {sujet}")
            print(f"Template: {template_name}")
            print(f"Contenu (texte):\n{text_content[:200]}...")
            print("=" * 50)
            return True

        # En production, envoyer réellement
        send_mail(
            subject=sujet,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinataire],
            html_message=html_content,
            fail_silently=False,
        )
        return True

    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False


# Fonctions spécifiques pour chaque type d'email


def envoyer_email_bienvenue(utilisateur):
    """Envoie l'email de bienvenue"""
    return envoyer_email_html(
        destinataire=utilisateur.email,
        sujet=f"🌟 Bienvenue sur DiapalSen, {utilisateur.first_name} !",
        template_name="emails/bienvenue.html",
        context={"utilisateur": utilisateur},
    )


def envoyer_email_contribution_confirmee(contribution):
    """Envoie l'email de confirmation de contribution"""
    return envoyer_email_html(
        destinataire=contribution.contributeur.email,
        sujet=f"✅ Votre contribution de {contribution.montant} FCFA est confirmée",
        template_name="emails/contribution_confirmee.html",
        context={"contribution": contribution},
    )


def envoyer_email_projet_valide(projet):
    """Envoie l'email de validation de projet"""
    return envoyer_email_html(
        destinataire=projet.porteur.email,
        sujet=f"🎉 Votre projet '{projet.titre}' est validé !",
        template_name="emails/projet_valide.html",
        context={"projet": projet},
    )


def envoyer_email_projet_rejete(projet, motif):
    """Envoie l'email de rejet de projet"""
    # Template à créer si besoin
    contenu = f"""
    Bonjour {projet.porteur.first_name},
    
    Votre projet "{projet.titre}" n'a malheureusement pas pu être validé.
    
    Motif : {motif}
    
    Vous pouvez modifier votre projet et le soumettre à nouveau.
    
    L'équipe DiapalSen
    """

    from django.core.mail import send_mail

    return send_mail(
        subject=f"Projet '{projet.titre}' - Validation non accordée",
        message=contenu,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[projet.porteur.email],
        fail_silently=False,
    )
