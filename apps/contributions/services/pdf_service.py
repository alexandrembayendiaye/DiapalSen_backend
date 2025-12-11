"""
Service de génération de reçus PDF pour les contributions
"""
import os
import qrcode
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFService:
    """Service pour générer les reçus PDF des contributions"""

    @staticmethod
    def generer_recu_pdf(contribution):
        """
        Génère un reçu PDF pour une contribution et le sauvegarde
        
        Args:
            contribution: Instance du modèle Contribution
            
        Returns:
            str: Chemin relatif du fichier PDF généré
        """
        # Créer un buffer en mémoire
        buffer = BytesIO()
        
        # Créer le canvas PDF
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Ajouter le contenu
        PDFService._ajouter_header(p, width, height)
        PDFService._ajouter_titre(p, width, height)
        PDFService._ajouter_infos_contribution(p, contribution, width, height)
        PDFService._ajouter_qr_code(p, contribution, width, height)
        PDFService._ajouter_footer(p, width, height)
        
        # Finaliser le PDF
        p.showPage()
        p.save()
        
        # Sauvegarder le fichier
        buffer.seek(0)
        filename = f"recu_{contribution.reference_paiement}.pdf"
        contribution.recu_pdf.save(filename, ContentFile(buffer.read()), save=True)
        
        return contribution.recu_pdf.name

    @staticmethod
    def _ajouter_header(p, width, height):
        """Ajoute l'en-tête avec le logo et les informations DiapalSen"""
        # Ligne de séparation en haut
        p.setStrokeColor(colors.HexColor("#28a745"))
        p.setLineWidth(3)
        p.line(2*cm, height - 2*cm, width - 2*cm, height - 2*cm)
        
        # Titre DiapalSen
        p.setFont("Helvetica-Bold", 24)
        p.setFillColor(colors.HexColor("#28a745"))
        p.drawCentredString(width/2, height - 3*cm, "DiapalSen")
        
        # Sous-titre
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.grey)
        p.drawCentredString(width/2, height - 3.7*cm, "Plateforme de Crowdfunding Sénégalaise")

    @staticmethod
    def _ajouter_titre(p, width, height):
        """Ajoute le titre du document"""
        p.setFont("Helvetica-Bold", 18)
        p.setFillColor(colors.black)
        p.drawCentredString(width/2, height - 5.5*cm, "REÇU DE CONTRIBUTION")
        
        # Date d'émission
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.grey)
        date_emission = datetime.now().strftime("%d/%m/%Y à %H:%M")
        p.drawCentredString(width/2, height - 6.2*cm, f"Émis le {date_emission}")

    @staticmethod
    def _ajouter_infos_contribution(p, contribution, width, height):
        """Ajoute les informations détaillées de la contribution"""
        y_position = height - 8*cm
        left_margin = 3*cm
        
        # Cadre pour les informations
        p.setStrokeColor(colors.HexColor("#e0e0e0"))
        p.setLineWidth(1)
        p.rect(2.5*cm, y_position - 7*cm, width - 5*cm, 6.5*cm, stroke=1, fill=0)
        
        # Référence de paiement
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Référence de paiement :")
        p.setFont("Helvetica", 12)
        p.setFillColor(colors.HexColor("#28a745"))
        p.drawString(left_margin + 6*cm, y_position, contribution.reference_paiement)
        
        y_position -= 1.2*cm
        
        # Montant
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Montant :")
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor("#28a745"))
        montant_str = f"{int(contribution.montant):,} FCFA".replace(",", " ")
        p.drawString(left_margin + 6*cm, y_position, montant_str)
        
        y_position -= 1.2*cm
        
        # Projet soutenu
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Projet soutenu :")
        p.setFont("Helvetica", 11)
        p.setFillColor(colors.black)
        
        # Gérer les titres longs
        titre_projet = contribution.projet.titre
        if len(titre_projet) > 50:
            titre_projet = titre_projet[:47] + "..."
        p.drawString(left_margin + 6*cm, y_position, titre_projet)
        
        y_position -= 1.2*cm
        
        # Contributeur
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Contributeur :")
        p.setFont("Helvetica", 11)
        nom_contributeur = contribution.contributeur_nom_affiche
        p.drawString(left_margin + 6*cm, y_position, nom_contributeur)
        
        y_position -= 1.2*cm
        
        # Date de contribution
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Date de contribution :")
        p.setFont("Helvetica", 11)
        date_contrib = contribution.date_contribution.strftime("%d/%m/%Y à %H:%M")
        p.drawString(left_margin + 6*cm, y_position, date_contrib)
        
        y_position -= 1.2*cm
        
        # Moyen de paiement
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Moyen de paiement :")
        p.setFont("Helvetica", 11)
        moyen = contribution.get_moyen_paiement_display()
        p.drawString(left_margin + 6*cm, y_position, moyen)
        
        y_position -= 1.2*cm
        
        # Statut
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(left_margin, y_position, "Statut :")
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(colors.HexColor("#28a745"))
        p.drawString(left_margin + 6*cm, y_position, "✓ VALIDÉ")

    @staticmethod
    def _ajouter_qr_code(p, contribution, width, height):
        """Ajoute un QR code pour vérification"""
        from reportlab.lib.utils import ImageReader
        
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        
        # URL de vérification (à adapter selon votre domaine)
        verification_url = f"https://diapalsen.com/verifier/{contribution.reference_paiement}"
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Créer l'image du QR code
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder temporairement dans un buffer
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Utiliser ImageReader pour lire le buffer
        qr_image_reader = ImageReader(qr_buffer)
        
        # Dessiner le QR code sur le PDF
        qr_size = 3*cm
        qr_x = width - 5*cm
        qr_y = height - 16*cm
        
        p.drawImage(qr_image_reader, qr_x, qr_y, width=qr_size, height=qr_size)
        
        # Texte sous le QR code
        p.setFont("Helvetica", 8)
        p.setFillColor(colors.grey)
        p.drawCentredString(qr_x + qr_size/2, qr_y - 0.5*cm, "Scanner pour vérifier")


    @staticmethod
    def _ajouter_footer(p, width, height):
        """Ajoute le pied de page"""
        y_footer = 3*cm
        
        # Ligne de séparation
        p.setStrokeColor(colors.HexColor("#e0e0e0"))
        p.setLineWidth(1)
        p.line(2*cm, y_footer + 1*cm, width - 2*cm, y_footer + 1*cm)
        
        # Message de remerciement
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(colors.HexColor("#28a745"))
        p.drawCentredString(width/2, y_footer + 0.3*cm, "Merci pour votre soutien !")
        
        # Informations légales
        p.setFont("Helvetica", 8)
        p.setFillColor(colors.grey)
        p.drawCentredString(width/2, y_footer - 0.5*cm, "DiapalSen - Plateforme de crowdfunding sénégalaise")
        p.drawCentredString(width/2, y_footer - 0.9*cm, "Email: contact@diapalsen.com | Tél: +221 XX XXX XX XX")
        p.drawCentredString(width/2, y_footer - 1.3*cm, "Ce document est généré automatiquement et certifie la réception de votre contribution.")
