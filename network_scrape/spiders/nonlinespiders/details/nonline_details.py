import scrapy
from scraper.models import NonlineListings
from scrapy import Request
from scrapy.spidermiddlewares.httperror import HttpError
from django.db.models import Q
import django
import os
import sys
import json
from w3lib.html import replace_tags

# Ustawienia Django
sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'NetworkMonitoring.settings'
django.setup()

class NonlineDetailSpider(scrapy.Spider):
    name = 'nonline_details'
    allowed_domains = ['nieruchomosci-online.pl']
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
            'network_scrape.pipelines.NonlineDetailsPipeline': 300,
        },
        'CONCURRENT_REQUESTS': 16,  # Zwiększenie liczby równoległych żądań
        'DOWNLOAD_DELAY': 1,  # Ustawienie opóźnienia między żądaniami
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtruj ogłoszenia, które mają puste pole z linkami do zdjęć lub tytułem
        self.ads = list(NonlineListings.objects.order_by('id'))

    def start_requests(self):
        if not self.ads:
            self.logger.info("No ads to process.")
            return

        for ad in self.ads:
            self.logger.info(f"Processing ad: {ad.url}")
            yield Request(url=ad.url, callback=self.parse, meta={'id': ad.id}, errback=self.handle_error)

    def handle_error(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 410:
                ad_id = response.meta.get('id')
                item = {'id': ad_id, 'isActive': False}
                yield item

    def parse(self, response):
        ad_id = response.meta['id']
        ad_data = self.parse_html(response)

        if ad_data:
            ad_data['id'] = ad_id
            self.logger.info(f"Extracted data for ad id {ad_id}: {ad_data}")
            yield ad_data
        else:
            self.logger.error(f"Failed to extract data for ad id {ad_id}")

    def parse_html(self, response):
        ad_data = {}
        try:
            # Informacje główne
            ad_data['title'] = response.css('h1.header-b.mod-c::text').get().strip()
            ad_data['address'] = ' '.join(response.css('li.adress span *::text').getall()).strip()
            ad_data['updated_at'] = response.css('p.current-as strong::text').get().strip()
            ad_data['price'] = response.css('p.info-primary-price::text').get().strip()
            ad_data['price_per_m2'] = response.css('p.info-secondary-price::text').get().strip()
            ad_data['square_footage'] = response.css('p.info-area::text').get().strip()

            # Pobieranie danych z tabeli "Szczegóły ogłoszenia"
            ad_data['floor'] = response.xpath('//li[strong[contains(text(),"Rozkład mieszkania:")]]/span/text()').get()
            ad_data['rooms'] = response.xpath('//li[strong[contains(text(),"Charakterystyka mieszkania:")]]/span/text()').re_first(r'(\d+)\s*poko(?:je|i)')
            ad_data['build_year'] = response.xpath('//li[strong[contains(text(),"Budynek:")]]/span/text()').re_first(r'rok budowy:\s*(\d{4})')
            ad_data['rent'] = response.xpath('//li[strong[contains(text(),"Czynsz:")]]/span/text()').get()
            ad_data['market_type'] = response.xpath('//li[strong[contains(text(),"Rynek:")]]/span/text()').get()
            ad_data['balcony'] = response.xpath('//li[strong[contains(text(),"Powierzchnia dodatkowa:")]]/span/text()').get()
            ad_data['security'] = response.xpath('//li[strong[contains(text(),"Bezpieczeństwo:")]]/span/text()').get()
            ad_data['media'] = response.xpath('//ul/li[strong[contains(text(),"Media:")]]/span/text()').get()
            ad_data['ownership_form'] = response.xpath('//li[strong[contains(text(),"Forma własności:")]]/span/text()').get()
            ad_data['estate_condition'] = response.xpath('//li[strong[contains(text(),"Charakterystyka mieszkania:")]]/span/text()').re_first(r'stan:\s*(\w+)')
            ad_data['equipment'] = response.xpath('//li[strong[contains(text(),"Wyposażenie:")]]/span/a/text()').get()
            ad_data['neighborhood'] = response.xpath('//li[strong[contains(text(),"W pobliżu:")]]/span/text()').get()
            ad_data['windows'] = response.xpath('//li[span[contains(text(),"okna:")]]/span/text()').re_first(r'okna:\s*(\w+)')
            ad_data['building_material'] = response.xpath('//li[span[contains(text(),"technika budowy:")]]/span/text()').re_first(r'technika budowy:\s*(\w+/[\w/]+)')
            ad_data['elevator'] = response.xpath('//li[span[contains(text(),"winda")]]/span/text()').get()
            ad_data['heating_type'] = response.xpath('//li[strong[contains(text(),"Media:")]]/span/text()').re_first(r'ogrzewanie:\s*(\w+)')
            ad_data['parking_space'] = response.xpath('//li[strong[contains(text(),"Miejsce parkingowe:")]]/span/a/text()').get()
            ad_data['available_from'] = response.xpath('//li[strong[contains(text(),"Dostępne:")]]/span/text()').get()
            ad_data['building_type'] = response.xpath('//li[strong[contains(text(),"Budynek:")]]/span/text()').re_first(r'(\w+); rok budowy')
            # ad_data['advertiser_type'] = response.xpath('//li[strong[contains(text(), "Źródło:")]/span/text()').get()
           
           
            # Pobieranie linków do zdjęć
            image_urls = response.xpath('//ul[@class="box-gallery"]//img/@src').getall()
            data_image_urls = [url for url in response.xpath('//ul[@class="box-gallery"]//li/@data-image').getall() if url]

            # Połącz wszystkie linki
            all_image_urls = image_urls + data_image_urls
            ad_data['original_image_urls'] = list(set(all_image_urls))  # Usunięcie duplikatów

            # Logowanie dla debugowania
            self.logger.info(f"Image URLs (src): {image_urls}")
            self.logger.info(f"Image URLs (data-image): {data_image_urls}")            

            # Pobieranie opisu
            description_html = response.css('div.estate-desc-more p').getall()
            if description_html:
                description = ''.join(description_html).replace('<br>', '\n').replace('&nbsp;', ' ')
                description = replace_tags(description, '')
                ad_data['description'] = description.strip()

        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")

        return ad_data
