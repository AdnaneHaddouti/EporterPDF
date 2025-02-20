import requests

# 🔧 Configuration : URL de Grafana et Token API
GRAFANA_CLOUD_INSTANCE_URL = "https://adnanehaddoutidev.grafana.net"
GRAFANA_SOURCE_TOKEN = "XXX"  # 🔴 Remplace par ton API Key

# 🔧 Configuration : URL de Grafana et Token API

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_SOURCE_TOKEN}",
    "Content-Type": "application/json"
}

def get_dashboards():
    """Récupère la liste des dashboards disponibles."""
    url = f"{GRAFANA_CLOUD_INSTANCE_URL}/api/search"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return None

# Test de récupération des dashboards
dashboards = get_dashboards()
if dashboards:
    print("\n📊 Liste des Dashboards disponibles :")
    for dash in dashboards:
        print(f" - {dash['title']} (UID: {dash['uid']})")
else:
    print("❌ Impossible de récupérer les dashboards. Vérifie ton API Key.")
