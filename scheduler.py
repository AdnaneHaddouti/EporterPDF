import schedule
import time
from datetime import datetime
from pdf_generator import generate_pdf


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