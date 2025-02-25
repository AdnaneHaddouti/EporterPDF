import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from grafana_api import fetch_dashboard_data, fetch_dashboard_image

from config import OUTPUT_DIR,DASHBOARD_UID


def generate_pdf():
    """Génère un PDF avec les informations et l’image du dashboard."""
    print("📄 Génération du rapport PDF...")
    
    dashboard_data = fetch_dashboard_data()
    if not dashboard_data:
        return

    # Plage des 30 derniers jours
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    pdf_file = f"{OUTPUT_DIR}/Usage_Insights_Overview_{start_date}_to_{end_date}.pdf"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Titre du rapport avec la plage des 30 derniers jours
    story.append(Paragraph(f"Rapport sur les 30 derniers jours - Usage Insights ({start_date} au {end_date})", styles['Title']))
    story.append(Spacer(1, 20))

    title = dashboard_data.get("dashboard", {}).get("title", "N/A")
    story.append(Paragraph(f"Dashboard : {title}", styles['Heading2']))
    story.append(Paragraph(f"UID : {DASHBOARD_UID}", styles['Normal']))
    story.append(Spacer(1, 12))

    image_path = fetch_dashboard_image()
    if image_path and os.path.exists(image_path):
        story.append(Paragraph("Aperçu du dashboard :", styles['Heading3']))
        story.append(Image(image_path, width=500, height=250))
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("⚠️ Impossible de récupérer l’image du dashboard.", styles['Normal']))

    story.append(Paragraph("Ce rapport est généré automatiquement chaque mois.", styles['Italic']))

    # Générer le PDF
    doc.build(story)
    print(f"✅ PDF généré avec succès : {pdf_file}")

    # Supprimer l'image temporaire si elle existe
    if image_path and os.path.exists(image_path):
        os.remove(image_path)
