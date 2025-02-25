from pdf_generator import PDFGenerator
from scheduler import schedule_report
import time

def main():
    
    generator = PDFGenerator()
    generator.generate_pdf()
    
    # Planifier les tâches récurrentes
    ## schedule_report()
    # Maintenir le script en vie pour les tâches planifiées
    ## while True:
        ## time.sleep(60)
    print("✅ Script terminé avec succès.")


if __name__ == "__main__":
    main() 