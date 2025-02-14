import os
import psutil
import requests    

GRAFANA_URL = "https://adnanehaddoutidev.grafana.net/api/health"

def is_vscode_running():
    """Vérifie si VS Code est en cours d'exécution."""
    for process in psutil.process_iter(['name']):
        if process.info['name'] and "Code" in process.info['name']:
            return True
    return False

def is_python_running_in_vscode():
    """Vérifie si Python est exécuté dans VS Code en cherchant 'VSCODE' dans les variables d'environnement."""
    return any("VSCODE" in key for key in os.environ.keys())

def is_grafana_running():
    """Vérifie si Grafana est accessible via son API."""
    try:
        response = requests.get(GRAFANA_URL, timeout=3)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        pass
    return False

if __name__ == "__main__":
    vscode_status = is_vscode_running()
    python_vscode_status = is_python_running_in_vscode()
    grafana_status = is_grafana_running()

    print("🔍 Vérification des connexions :\n")
    print(f"🖥️  VS Code en cours d'exécution : {'✅ Oui' if vscode_status else '❌ Non'}")
    print(f"🐍 Python exécuté dans VS Code : {'✅ Oui' if python_vscode_status else '❌ Non'}")
    print(f"📊 Grafana est accessible : {'✅ Oui' if grafana_status else '❌ Non'}")

    if not vscode_status:
        print("\n⚠️  VS Code ne semble pas être en cours d'exécution.")
    if not python_vscode_status:
        print("\n⚠️  Python ne semble pas être exécuté via VS Code.")
    if not grafana_status:
        print("\n⚠️  Grafana ne semble pas être accessible. Vérifie s'il est bien démarré sur 10.30.1.160:1994.")
