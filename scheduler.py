import schedule
import time
from pdf_generator import PDFGenerator

def schedule_report():
    
    pdf_generator = PDFGenerator()

    # Planifier la génération mensuelle
    schedule.every().day.at("00:00").do(pdf_generator.generate_pdf)

    while True:
        schedule.run_pending()
        time.sleep(1)