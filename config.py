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


HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}
