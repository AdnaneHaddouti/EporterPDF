import requests
import sys
import io
import os
import json
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

# 🔍 Récupérer les rows d'un dashboard spécifique par son UID
def get_dashboard_rows(dashboard_uid):
    url = f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        if not response.text.strip():
            print("❌ La réponse de Grafana est vide.")
            return

        dashboard_details = response.json()
        dashboard_title = dashboard_details.get("dashboard", {}).get("title", "Sans titre")
        panels = dashboard_details.get("dashboard", {}).get("panels", [])

        # Afficher la structure JSON pour débogage
        # print(json.dumps(dashboard_details, indent=2))

        if not panels:
            print(f"ℹ️ Aucun panel trouvé dans le dashboard '{dashboard_title}'.")
            return

        print(f"📊 Structure du Dashboard '{dashboard_title}' (UID: {dashboard_uid}) :")

        # Dictionnaire pour organiser les panels par row
        rows_with_panels = {}

        # Parcourir tous les panels
        current_row = None
        for panel in panels:
            panel_type = panel.get("type", "Type inconnu")
            panel_title = panel.get("title", "Sans titre")

            # Si le panel est de type "row", c'est une nouvelle row
            if panel_type == "row":
                current_row = panel_title
                rows_with_panels[current_row] = []
            # Sinon, l'ajouter à la row actuelle
            elif current_row:
                rows_with_panels[current_row].append({
                    "title": panel_title,
                    "type": panel_type
                })

        # Afficher les panels organisés par row
        for row_title, panels_in_row in rows_with_panels.items():
            print(f"➡️  Row: {row_title}")
            for panel in panels_in_row:
                print(f"  🔍 Panel: {panel['title']} (Type: {panel['type']})")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ Erreur HTTP : {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Erreur de requête : {req_err}")
    except ValueError as json_err:
        print(f"❌ Erreur lors de l'analyse JSON : {json_err}")
    except Exception as e:
        print(f"❌ Une erreur inattendue s'est produite : {e}")

if __name__ == "__main__":
    # Vérifier la connexion à Grafana
    check_grafana_connection()

    # Récupérer la liste des dashboards
    get_dashboards()

    # Demander à l'utilisateur de saisir l'UID d'un dashboard
    dashboard_uid = input("\n🔍 Entrez l'UID du dashboard pour récupérer ses rows : ")
    if dashboard_uid:
        get_dashboard_rows(dashboard_uid)
    else:
        print("❌ Aucun UID saisi.")