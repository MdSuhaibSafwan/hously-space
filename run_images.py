import sys
import os
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.base import JobLookupError
import django
from datetime import datetime, timedelta

# Ustaw zmienną środowiskową DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NetworkMonitoring.settings')  # Zmień 'NetworkMonitoring' na nazwę swojego projektu

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

def run_otodom_images():
    run_spider('otodom_images')

def run_nonline_images():
    run_spider('nonline_images')

def run_merge_listings():
    try:
        merge_listings_to_network_monitoring()
        print("Listings merged successfully.")
    except Exception as e:
        print(f"Error during merging listings: {e}")

def start_jobs():
    scheduler.add_job(run_otodom_images, 'interval', minutes=60, id='otodom_images_job')
    scheduler.add_job(run_nonline_images, 'interval', minutes=60, id='nonline_images_job')

def stop_jobs():
    try:
        scheduler.remove_job('otodom_images_job')
        scheduler.remove_job('nonline_images_job')
    except JobLookupError:
        print("Jobs not found")

if __name__ == '__main__':
    scheduler = BlockingScheduler()

    # Start jobs initially and run them immediately
    start_jobs()
    run_otodom_images()
    run_nonline_images()

    # Schedule stopping jobs after 1 hour
    scheduler.add_job(stop_jobs, DateTrigger(run_date=datetime.now() + timedelta(hours=1)))

    # Schedule starting jobs again after 1 hour 10 minutes
    scheduler.add_job(start_jobs, DateTrigger(run_date=datetime.now() + timedelta(hours=1, minutes=10)))

    try:
        print("Starting scheduler...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
