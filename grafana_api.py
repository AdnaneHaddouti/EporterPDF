import requests
import os
from datetime import datetime, timedelta
from config import HEADERS, GRAFANA_URL, DASHBOARD_UID, TEMP_IMAGE
from PIL import Image

class GrafanaAPI:

    def fetch_dashboard_data(self):
        url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
        print(f"🔍 Tentative de récupération des métadonnées à l'URL : {url}")
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            print(f"🗃️  Métadonnées récupérées avec succès (Code HTTP: {response.status_code})")
            return response.json()
        else:
            print(f"❌ Erreur HTTP {response.status_code} lors de la récupération des métadonnées : {response.text}")
            return None

    def get_dashboards(self):
        url = f"{GRAFANA_URL}/api/search"
        print(f"🔍 Tentative de récupération des dashboards à l'URL : {url}")
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

    def get_row_screenshot(self, dashboard_uid, row_title, row_panels):
        if not row_panels:
            print(f"❌ Erreur : Aucun panel trouvé pour la row '{row_title}'.")
            print(f"🔍 Détails des panels : {row_panels}")  # Log supplémentaire pour examiner les données
            return None

        # Trier les panels par position y pour choisir le premier panel de la row
        row_panels.sort(key=lambda p: p.get("gridPos", {}).get("y", 9999))
        reference_panel = row_panels[0]  # Premier panel en haut de la row

        # Vérifier que le panel a une position y
        panel_y = reference_panel.get("gridPos", {}).get("y")
        panel_height = sum(p.get("gridPos", {}).get("h", 5) for p in row_panels) * 50  # Facteur d'échelle

        if panel_y is None:
            print(f"❌ Erreur : Impossible de déterminer la position pour la row '{row_title}'.")
            return None

        print(f"📸 Capture d'écran pour la row '{row_title}' avec position y = {panel_y}")
        print(f"🔍 Hauteur calculée de la row '{row_title}': {panel_height}")

        # Générer une image avec la position Y et hauteur dynamique
        image_path = self.fetch_screenshot_by_position(dashboard_uid, row_title, panel_y, panel_height)

        if image_path is None:
            print(f"❌ Échec de la capture pour la row '{row_title}'.")
            return None

        return image_path

    def crop_image(self, full_image_path, row_title, crop_top, crop_height):
        """
        Ouvre l'image complète et recadre la zone de la row :
        - crop_top : position verticale de départ (en pixels)
        - crop_height : hauteur de la zone (en pixels)
        """
        try:
            img = Image.open(full_image_path)
            width, height = img.size
            box = (0, crop_top, width, crop_top + crop_height)
            cropped_img = img.crop(box)
            cropped_path = f"./screenshots/{row_title.replace(' ', '_')}_cropped.png"
            cropped_img.save(cropped_path)
            return cropped_path
        except Exception as e:
            print(f"❌ Erreur lors du recadrage de l'image pour {row_title}: {e}")
            return None
        
    def fetch_screenshot_by_position(self, dashboard_uid, row_title, position_y, row_height, row_id=None):
        """
        Capture une portion du dashboard en spécifiant la position Y et la hauteur.
        Vous pouvez spécifier un ID pour chaque row.
        """
        current_time = datetime.now()
        from_time = int((current_time - timedelta(days=30)).timestamp() * 1000)  # il y a 30 jours
        to_time = int(current_time.timestamp() * 1000)  # maintenant
       
        screenshot_url = (
            f"{GRAFANA_URL}/render/d/{dashboard_uid}"
            f"?from={from_time}&to={to_time}&theme=light&width=1000&height={row_height}&y={position_y}"
        )
        
        print(f"        🔍 Tentative de capture à l'URL : {screenshot_url}")  # Log de l'URL pour débogage
        
        try:
            response = requests.get(screenshot_url, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                os.makedirs("./screenshots", exist_ok=True)
                
                # Utilisation de l'ID spécifié si fourni, sinon génération d'un nom à partir du titre
                row_id = row_id if row_id else row_title.replace(' ', '_')
                image_path = f"./screenshots/{row_id}.png"
                
                with open(image_path, "wb") as file:
                    file.write(response.content)
                
                print(f"        ✅ Capture réussie : {image_path} (Taille : {len(response.content)} octets)")
                return image_path
            else:
                print(f"❌ Échec de la capture pour la row '{row_title}' (y={position_y}). Code HTTP : {response.status_code}")
                print(f"🔍 Détails de l'erreur : {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la requête : {e}")
            return None
        
    def fetch_full_dashboard_screenshot(self, dashboard_uid, full_height):
        """
        Capture l'intégralité du dashboard en précisant une hauteur suffisante.
        """
        current_time = datetime.now()
        from_time = int((current_time - timedelta(days=30)).timestamp() * 1000)
        to_time = int(current_time.timestamp() * 1000)
        
        screenshot_url = (
            f"{GRAFANA_URL}/render/d/{dashboard_uid}"
            f"?from={from_time}&to={to_time}&theme=light&width=1000&height={full_height}"
        )
        try:
            response = requests.get(screenshot_url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                os.makedirs("./screenshots", exist_ok=True)
                full_path = "./screenshots/full_dashboard.png"
                with open(full_path, "wb") as file:
                    file.write(response.content)
                return full_path
            else:
                print(f"❌ Erreur lors de la capture complète du dashboard - Code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de requête lors de la capture complète du dashboard: {e}")
            return None