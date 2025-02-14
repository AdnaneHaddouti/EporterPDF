import requests

# 🔧 Configuration : URL de Grafana et Token API
GRAFANA_CLOUD_INSTANCE_URL = "https://adnanehaddoutidev.grafana.net"
GRAFANA_SOURCE_TOKEN = "eyJUb2tlbiI6ImdsY19leUp2SWpvaU1UQTFOVGszTXlJc0ltNGlPaUpuY21GbVlXNWhMV05zYjNWa0xXMXBaM0poZEdsdmJuTXRPRFU1TVRNeklpd2lheUk2SWpoQk0ySXpNemc1UkV4Wlp6UkhTRzlKTkdZNE5VdG9jQ0lzSW0waU9uc2ljaUk2SW5CeWIyUXRkWE10WldGemRDMHdJbjE5IiwiSW5zdGFuY2UiOnsiU3RhY2tJRCI6ODU5MTMzLCJTbHVnIjoiYWRuYW5laGFkZG91dGlkZXYiLCJSZWdpb25TbHVnIjoicHJvZC11cy1lYXN0LTAiLCJDbHVzdGVyU2x1ZyI6InByb2QtdXMtZWFzdC0wIn19"  # 🔴 Remplace par ton API Key

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
