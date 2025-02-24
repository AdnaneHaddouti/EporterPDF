import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import schedule
from datetime import timedelta
import time
from datetime import datetime
import os
import sys


from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()



API_TOKEN = os.getenv("API_TOKEN")
GRAFANA_URL = os.getenv("GRAFANA_URL")
DASHBOARD_UID = os.getenv("DASHBOARD_UID")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
TEMP_IMAGE = os.getenv("TEMP_IMAGE")


# Configuration
if not API_TOKEN:
    print("❌ Erreur : Le token API Grafana n'est pas défini !")
    sys.exit(1)

# Headers pour l’authentification
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

def fetch_dashboard_data():
    """Récupère les métadonnées du dashboard via l’API Grafana."""
    url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        print("✅ Métadonnées du dashboard récupérées avec succès")
        return response.json()
    else:
        print(f"❌ Erreur lors de la récupération du dashboard : {response.status_code}")
        return None

def fetch_dashboard_image():
    """Récupère une image rendue du dashboard via l’API de rendu."""
    current_time = datetime.now()
    from_time = int((current_time - timedelta(days=30)).timestamp() * 1000)
    to_time = int(current_time.timestamp() * 1000)

    render_url = f"{GRAFANA_URL}/render/d/{DASHBOARD_UID}?width=1000&height=500&from={from_time}&to={to_time}"
    response = requests.get(render_url, headers=HEADERS)
    
    if response.status_code == 200:
        with open(TEMP_IMAGE, "wb") as f:
            f.write(response.content)
        print("✅ Image du dashboard récupérée avec succès")
        return TEMP_IMAGE
    else:
        print(f"❌ Erreur lors du rendu de l’image : {response.status_code}")
        return None

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


def get_dashboards():
    """Affiche la liste des dashboards disponibles sur Grafana."""
    url = f"{GRAFANA_URL}/api/search"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        if not response.text.strip():
            print("❌ La réponse de Grafana est vide.")
            return

        dashboards = response.json()
        print("📊 Liste des Dashboards disponibles :")
        for dashboard in dashboards:
            print(f"- {dashboard.get('title', 'Sans titre')} (UID: {dashboard.get('uid')})")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ Erreur HTTP : {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Erreur de requête : {req_err}")
    except ValueError as json_err:
        print(f"❌ Erreur lors de l'analyse JSON : {json_err}")

def monthly_report():
    print(f"⏰ Début de la génération du rapport mensuel ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    generate_pdf()

def check_and_run_monthly_report():
    """Vérifie si c'est le 1er du mois avant d'exécuter le rapport."""
    if datetime.now().day == 1:
        monthly_report()

# Planification : Vérifie chaque jour à minuit et exécute seulement le 1er du mois
schedule.every().day.at("00:00").do(monthly_report)

# Pour tester rapidement toutes les 10 secondes :
schedule.every(10).seconds.do(monthly_report)

print("🚀 Script démarré. En attente de la prochaine exécution...")

while True:
    print("⏳ En attente d'une tâche planifiée...")
    schedule.run_pending()
    time.sleep(60)  # Vérifie les tâches planifiées toutes les minutes

