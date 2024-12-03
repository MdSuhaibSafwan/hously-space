import sys
import os
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import django

# Ustaw zmienną środowiskową DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NetworkMonitoring.settings')  # Zmień 'your_project_name' na nazwę swojego projektu

# Zainicjuj Django
django.setup()

# Dodaj pełną ścieżkę do katalogu głównego projektu
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'network_scrape'))
sys.path.append(os.path.join(project_path, 'NetworkMonitoring'))

# Importuj funkcję merge_listings_to_network_monitoring po zainicjowaniu Django
from scraper.api.advertisments.merge_listings import merge_listings_to_network_monitoring

def run_spider(spider_name):
    subprocess.run(['scrapy', 'crawl', spider_name])

def run_otodom_mieszkania():
    run_spider('otodom_mieszkania')
    run_otodom_domy()

def run_otodom_domy():
    run_spider('otodom_domy')
    run_otodom_kawalerki()

def run_otodom_kawalerki():
    run_spider('otodom_kawalerki')
    run_spider('otodom_details')
    # run_spider('otodom_images')
    
def run_nonline_urls():
    run_spider('nonline_urls')
    run_nonline_details()
    
def run_nonline_details():
    run_spider('nonline_details')
    

def run_merge_listings():
    try:
        merge_listings_to_network_monitoring()
        print("Listings merged successfully.")
    except Exception as e:
        print(f"Error during merging listings: {e}")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(run_otodom_mieszkania, IntervalTrigger(minutes=10))
    scheduler.add_job(run_nonline_urls, IntervalTrigger(minutes=10))
    scheduler.add_job(run_merge_listings, IntervalTrigger(minutes=15)) 

    try:
        print("Starting scheduler...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
