from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta
from grafana_api import GrafanaAPI 
from config import OUTPUT_DIR
import os

from config import OUTPUT_DIR,DASHBOARD_UID

class PDFGenerator:

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.api = GrafanaAPI()
    
    def generate_pdf(self):
        print("🚀 Script démarré. En attente de la prochaine exécution...")
        print("📄 Génération du rapport PDF...")
        
        dashboard_data = self.api.fetch_dashboard_data() 
        if not dashboard_data:
            return

        # Plage des 30 derniers jours
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        pdf_file = f"{OUTPUT_DIR}/Usage_Insights_Overview_{start_date}_to_{end_date}.pdf"

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        story = []

        # Titre du rapport
        story.append(Paragraph(f"Rapport sur les 30 derniers jours - Usage Insights ({start_date} au {end_date})", self.styles['Title']))
        story.append(Spacer(1, 20))

        # Informations du dashboard
        title = dashboard_data.get("dashboard", {}).get("title", "N/A")
        story.append(Paragraph(f"Dashboard : {title}", self.styles['Heading2']))
        story.append(Paragraph(f"UID : {DASHBOARD_UID}", self.styles['Normal']))
        story.append(Spacer(1, 12))

        # Image du dashboard
        image_path = self.api.fetch_dashboard_image()
        if image_path and os.path.exists(image_path):
            story.append(Paragraph("Aperçu du dashboard :", self.styles['Heading3']))
            story.append(Image(image_path, width=500, height=250))
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("⚠️ Impossible de récupérer l’image du dashboard.", self.styles['Normal']))

        # Générer le PDF
        doc.build(story)
        print(f"📂 PDF généré avec succès : {pdf_file}")

        # Supprimer l'image temporaire
        if image_path and os.path.exists(image_path):
            os.remove(image_path)