import requests
import sys
import io
import os

from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
GRAFANA_URL = os.getenv("GRAFANA_URL")


# Changer stdout pour gérer Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Vérification de la clé API
if not API_TOKEN:
    print("❌ Erreur : Le token API Grafana n'est pas défini !")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 🔍 Vérifier la connexion avec Grafana
def check_grafana_connection():
    url = f"{GRAFANA_URL}/api/health"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        print("✅ Connexion réussie à Grafana Cloud !")
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ Erreur HTTP : {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Erreur de requête : {req_err}")

# 🔍 Récupérer la liste des dashboards
def get_dashboards():
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

if __name__ == "__main__":
    check_grafana_connection()
    get_dashboards()
