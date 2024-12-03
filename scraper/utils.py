import requests
from django.conf import settings


def get_dynamic_scraping_from_hously_cloud():
    url = settings.HOUSLY_CLOUD_URL + "/web-scraper/scrape/"
    r = requests.get(url)
    data = r.json()

    return data
