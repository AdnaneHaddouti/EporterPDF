import requests
from datetime import datetime, timedelta
from config import HEADERS, GRAFANA_URL, DASHBOARD_UID, TEMP_IMAGE

# Récupère les métadonnées du dashboard via l’API Grafana.
def fetch_dashboard_data():
    url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        print("✅ Métadonnées du dashboard récupérées avec succès")
        return response.json()
    else:
        print(f"❌ Erreur lors de la récupération du dashboard : {response.status_code}")
        return None
    
# Fonction pour récupérer une image du dashboard
def fetch_dashboard_image():
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
    
# Fonction pour récupérer la liste des dashboards
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