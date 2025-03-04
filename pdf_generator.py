from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta
from grafana_api import GrafanaAPI
from config import OUTPUT_DIR, DASHBOARD_UID
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.api = GrafanaAPI()

    def generate_pdf(self):
        print("🚀 Script démarré. En attente de la prochaine exécution...")
        print("📄 Génération du rapport PDF...")

        # Plage des 30 derniers jours
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        pdf_file = f"{OUTPUT_DIR}/Usage_Insights_Overview_{start_date}_to_{end_date}.pdf"
                
        # Récupérer les données du dashboard
        dashboard_data = self.api.fetch_dashboard_data()
        if not dashboard_data:
            print("❌ Erreur : Impossible de récupérer les données du dashboard.")
            return
        
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

        # Récupération des panels
        panels = dashboard_data.get("dashboard", {}).get("panels", [])
        # Filtrer pour obtenir uniquement les rows
        rows = [panel for panel in panels if panel.get("type") == "row"]
        print(" ✅ Rows détectées :", [row.get("title") for row in rows])
        
        # Créer un mapping des panels associés à chaque row, en se basant sur leur position d'origine
        row_panels_map = {}
        current_row_y = None
        for panel in panels:
            if panel.get("type") == "row":
                current_row_y = panel.get("gridPos", {}).get("y")
                row_panels_map[current_row_y] = []
            elif current_row_y is not None:
                row_panels_map[current_row_y].append(panel)

        # Calculer la hauteur totale du dashboard pour capturer l'intégralité
        # On parcourt tous les panels pour obtenir le maximum de (y + h)
        # Définir un offset pour la capture
        offset_y = 218  # Ajustez cette valeur selon vos besoins

        # Calculer la hauteur totale du dashboard pour capturer l'intégralité
        # On parcourt tous les panels pour obtenir le maximum de (y + h)
        max_val = 0
        for panel in panels:
            gridPos = panel.get("gridPos", {})
            y_val = gridPos.get("y", 0)
            h_val = gridPos.get("h", 0)
            max_val = max(max_val, y_val + h_val)
        full_height = (max_val * 50) + offset_y  # Facteur d'échelle et ajout de l'offset

        # Capturer l'image complète du dashboard
        full_image_path = self.api.fetch_full_dashboard_screenshot(DASHBOARD_UID, full_height)
        if not full_image_path:
            print("❌ Erreur lors de la capture de l'image complète du dashboard.")
            return

        # Pour chaque row, recadrer l'image complète selon sa position et sa hauteur
        for row in rows:
            row_title = row.get("title", "Row")
            story.append(Paragraph(f"{row_title}", self.styles['Heading3']))
            
            # Obtenir la position d'origine et la hauteur depuis le dashboard
            # La position verticale (y) et la hauteur (h) sont en "grid units" : on multiplie par 50 pour avoir des pixels.
            gridPos = row.get("gridPos", {})
            row_y_units = gridPos.get("y", 0)
            row_y = (row_y_units * 50) + offset_y  # Ajout de l'offset
            print(f"    🔍 Position de la row '{row_title}': y={row_y}")

            # Récupérer les panels associés à cette row pour déterminer sa hauteur.
            row_panels = row_panels_map.get(row.get("gridPos", {}).get("y"), [])
            if not row_panels:
                print(f"❌ Erreur : Aucun panel trouvé pour la row '{row_title}'.")
                story.append(Paragraph("⚠️ Aucun panel trouvé pour cette row.", self.styles['Normal']))
                story.append(Spacer(1, 12))
                continue
            # La hauteur de la row est le maximum de "h" des panels multiplié par le facteur d'échelle
            row_height_units = max(p.get("gridPos", {}).get("h", 5) for p in row_panels)
            row_height = row_height_units * 50
            # Recadrer l'image complète pour obtenir la partie correspondant à cette row
            cropped_path = self.api.crop_image(full_image_path, row_title, row_y, row_height)
            print(f"    🖼️  Image recadrée pour '{row_title}' : {cropped_path} (y={row_y}, hauteur={row_height})")
            if cropped_path and os.path.exists(cropped_path):
                # Ajuster la taille dans le PDF si nécessaire
                story.append(RLImage(cropped_path, width=500, height=row_height // 2))
                story.append(Spacer(1, 12))
            else:
                story.append(Paragraph("⚠️ Échec du recadrage de l'image.", self.styles['Normal']))
                story.append(Spacer(1, 12))

        # Générer le PDF
        try:
            doc.build(story)
            print(f"📂 PDF généré avec succès : {pdf_file}")
        except Exception as e:
            print(f"❌ Erreur lors de la génération du PDF : {e}")

        # Affichage des rows
        print("🔍 Rows récupérées :")
        for idx, row in enumerate(rows, start=1):
            print(f"    {idx}️⃣   {row}")