import os
import scrapy
import requests
from scraper.models import ListingOtodom
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import django
import sys

# Ustawienia Django
sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'NetworkMonitoring.settings'
django.setup()

class OtodomDownloadImagesSpider(scrapy.Spider):
    name = 'otodom_images_copy'
    allowed_domains = ['*']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'ROBOTSTXT_OBEY': False,
        'ITEM_PIPELINES': {
            'network_scrape.pipelines.OtodomDownloadImagesPipeline': 400,
        },
        'CONCURRENT_REQUESTS': 16,  # Zwiększenie liczby równoległych żądań
        'DOWNLOAD_DELAY': 1,  # Ustawienie opóźnienia między żądaniami
    }
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pobierz ogłoszenia, które mają niepuste pole original_image_urls
        self.ads = list(ListingOtodom.objects.exclude(original_image_urls__isnull=True).exclude(original_image_urls__exact='').order_by('id'))

    def start_requests(self):
        if not self.ads:
            self.logger.info("No ads to process.")
            return

        for ad in self.ads:
            self.logger.info(f"Processing ad: {ad.id}")
            yield scrapy.Request(url='', callback=self.download_images, meta={'ad_id': ad.id, 'image_urls': ad.original_image_urls})

    def download_images(self, response):
        ad_id = response.meta['ad_id']
        image_urls = response.meta['image_urls']
        local_image_paths = []
        inactive = False

        for index, url in enumerate(image_urls):
            file_extension = url.split('.')[-1]
            image_filename = f"otodom_{ad_id}_{index}.{file_extension}"
            image_save_path = os.path.join(settings.MEDIA_ROOT, 'otodom_images', image_filename)

            if self.download_image(url, image_save_path):
                local_image_paths.append(os.path.join('otodom_images', image_filename))
            else:
                if response.status == 410:
                    inactive = True

        with transaction.atomic():
            listing = ListingOtodom.objects.get(id=ad_id)
            listing.images = local_image_paths
            if inactive:
                listing.isActive = False
                listing.inactive_date = timezone.now()
            listing.save()

    def download_image(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)
                return True
            else:
                self.logger.error(f"Failed to download image from {url} with status code {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error downloading image from {url}: {e}")
            return False
