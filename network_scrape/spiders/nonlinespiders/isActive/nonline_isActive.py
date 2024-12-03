import scrapy
from scraper.models import NonlineListings
from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from django.db.models import Q
import django
import os
import sys

# Ustawienia Django
sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'NetworkMonitoring.settings'
django.setup()

class OtodomDetailSpider(scrapy.Spider):
    name = 'nonline_isActive'
    allowed_domains = ['otodom.pl']
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
            'network_scrape.pipelines.OtodomIsActivePipeline': 300,
        },
        'CONCURRENT_REQUESTS': 16,  # Zwiększenie liczby równoległych żądań
        'DOWNLOAD_DELAY': 1,  # Ustawienie opóźnienia między żądaniami
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pobierz tylko aktywne ogłoszenia oraz te, które mają isActive ustawione na NULL
        self.ads = list(NonlineListings.objects.filter(Q(isActive=True) | Q(isActive__isnull=True)).order_by('id'))

    def start_requests(self):
        if not self.ads:
            self.logger.info("No ads to process.")
            return

        for ad in self.ads:
            self.logger.info(f"Processing ad: {ad.url}")
            yield Request(url=ad.url, callback=self.parse_html, meta={'id': ad.id}, errback=self.handle_error)

    def handle_error(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 410:
                ad_id = response.meta.get('id')
                item = {'id': ad_id, 'isActive': False}
                yield item

    def parse_html(self, response):
        ad_id = response.meta.get('id')
        ad_data = {}
        try:
            # Sprawdzanie, czy ogłoszenie jest niedostępne
            expired_alert = response.css('[data-cy="expired-ad-alert"]::text').get()
            if expired_alert and "To ogłoszenie jest już niedostępne" in expired_alert.strip():
                ad_data['isActive'] = False
                self.logger.info(f"Ad id {ad_id} is not active.")
            else:
                ad_data['isActive'] = True

            ad_data['id'] = ad_id  # Upewnij się, że ad_id jest w ad_data
            yield ad_data

        except Exception as e:
            self.logger.error(f"Error parsing HTML for ad id {ad_id}: {e}")
