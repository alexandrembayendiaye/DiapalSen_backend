import random
from decimal import Decimal
from datetime import datetime
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io


def simuler_paiement(moyen_paiement, montant, reference):
    """
    Simule un paiement avec les différents moyens de paiement sénégalais
    Retourne un dictionnaire avec le résultat de la simulation
    """

    # Simulation : 90% de succès, 10% d'échec
    succes = random.random() < 0.9

    if succes:
        # Simulation des données de paiement selon le moyen
        if moyen_paiement == "wave":
            donnees = {
                "transaction_id": f"WAVE_{random.randint(100000, 999999)}",
                "telephone": f"+221{random.randint(700000000, 799999999)}",
                "frais": float(montant) * 0.01,  # 1% de frais Wave
                "statut_api": "SUCCESS",
            }
        elif moyen_paiement == "orange_money":
            donnees = {
                "transaction_id": f"OM_{random.randint(100000, 999999)}",
                "telephone": f"+221{random.randint(770000000, 779999999)}",
                "frais": float(montant) * 0.015,  # 1.5% de frais Orange Money
                "statut_api": "COMPLETED",
            }
        elif moyen_paiement == "free_money":
            donnees = {
                "transaction_id": f"FREE_{random.randint(100000, 999999)}",
                "telephone": f"+221{random.randint(760000000, 769999999)}",
                "frais": float(montant) * 0.008,  # 0.8% de frais Free Money
                "statut_api": "PAID",
            }

        return {
            "succes": True,
            "statut": "valide",
            "message": "Paiement traité avec succès",
            "donnees": donnees,
        }
    else:
        # Simulation d'échec
        motifs_echec = [
            "Solde insuffisant",
            "Code PIN incorrect",
            "Compte temporairement bloqué",
            "Erreur réseau",
        ]

        return {
            "succes": False,
            "statut": "echoue",
            "message": f"Échec du paiement : {random.choice(motifs_echec)}",
            "donnees": {
                "error_code": random.randint(1001, 9999),
                "retry_possible": True,
            },
        }


def generer_recu_pdf(contribution):
    """
    Génère un reçu PDF pour une contribution
    """
    buffer = io.BytesIO()

    # Créer le PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "REÇU DE CONTRIBUTION - DIAPALSEN")

    # Ligne de séparation
    p.line(50, height - 70, width - 50, height - 70)

    # Informations du reçu
    y_position = height - 100
    p.setFont("Helvetica", 12)

    infos = [
        f"Référence : {contribution.reference_paiement}",
        f"Date : {contribution.date_contribution.strftime('%d/%m/%Y à %H:%M')}",
        f"Projet : {contribution.projet.titre}",
        f"Porteur : {contribution.projet.porteur.get_full_name()}",
        "",
        f"Contributeur : {contribution.contributeur_nom_affiche}",
        f"Montant : {contribution.montant:,.0f} FCFA",
        f"Moyen de paiement : {contribution.get_moyen_paiement_display()}",
        f"Statut : {contribution.get_statut_paiement_display()}",
    ]

    if contribution.message_soutien:
        infos.extend(["", f"Message : {contribution.message_soutien}"])

    for info in infos:
        p.drawString(50, y_position, info)
        y_position -= 20

    # Pied de page
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(
        50,
        50,
        "Merci pour votre soutien ! - DiapalSen, plateforme de crowdfunding sénégalaise",
    )

    p.showPage()
    p.save()

    buffer.seek(0)
    return ContentFile(
        buffer.read(), name=f"recu_{contribution.reference_paiement}.pdf"
    )
