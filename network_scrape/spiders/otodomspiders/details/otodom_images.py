import os
import scrapy
import requests
from scraper.models import ListingOtodom
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import django
import sys
from asgiref.sync import sync_to_async
from django.db.models import Q

# Ustawienia Django
sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'NetworkMonitoring.settings'
django.setup()

# Folder do zapisywania obrazów
IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, 'images/otodom_images')

# Upewnij się, że folder istnieje
os.makedirs(IMAGES_DIR, exist_ok=True)

class OtodomDownloadImagesSpider(scrapy.Spider):
    name = 'otodom_images'
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
        'DOWNLOAD_DELAY': 0.33,  # Ustawienie opóźnienia między żądaniami
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pobierz ogłoszenia, które mają niepuste pole original_image_urls i puste pole images
        self.ads = list(ListingOtodom.objects
                        .exclude(original_image_urls__isnull=True)
                        .exclude(original_image_urls__exact=[])
                        .exclude(original_image_urls__exact='')
                        .exclude(isActive=False)
                        .exclude(title__isnull=True)
                        .filter(Q(images__isnull=True) | Q(images=[]))
                        .order_by('id'))

    def start_requests(self):
        if not self.ads:
            self.logger.info("No ads to process.")
            return

        for ad in self.ads:
            self.logger.info(f"Processing ad: {ad.id}")
            yield scrapy.Request(
                url='http://example.com/',  # Używamy przykładowego URL, aby uniknąć błędu braku schematu
                callback=self.download_images,
                meta={'ad_id': ad.id, 'image_urls': ad.original_image_urls},
                dont_filter=True  # Nie filtruj tego URL, ponieważ jest przykładowy
            )

    async def download_images(self, response):
        ad_id = response.meta['ad_id']
        image_urls = response.meta['image_urls']
        local_image_paths = []
        inactive = False

        for index, url in enumerate(image_urls):
            # Zmień sposób tworzenia nazwy pliku, aby uniknąć znaków specjalnych
            image_filename = f"otodom_{ad_id}_{index}.webp"
            image_save_path = os.path.join(IMAGES_DIR, image_filename)

            if self.download_image(url.split(';')[0], image_save_path):
                local_image_paths.append(os.path.join('images/otodom_images', image_filename))
            else:
                if response.status_code == 410:
                    inactive = True

        await self.update_listing(ad_id, local_image_paths, inactive)

    @sync_to_async
    def update_listing(self, ad_id, local_image_paths, inactive):
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
