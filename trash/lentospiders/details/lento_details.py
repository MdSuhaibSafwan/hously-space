# import scrapy
# from scraper.models import ListingOtodom
# from scrapy import Request
# from scrapy.spidermiddlewares.httperror import HttpError
# from django.db.models import Q
# import django
# import os
# import sys
# import json

# # Ustawienia Django
# sys.path.append(os.path.dirname(os.path.abspath('.')))
# os.environ['DJANGO_SETTINGS_MODULE'] = 'NetworkMonitoring.settings'
# django.setup()

# class OtodomDetailSpider(scrapy.Spider):
#     name = 'lento_details'
#     allowed_domains = ['otodom.pl']
#     custom_settings = {
#         'DEFAULT_REQUEST_HEADERS': {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Accept-Language': 'en-US,en;q=0.9',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#         },
#         'ROBOTSTXT_OBEY': False,
#         'ITEM_PIPELINES': {
#             'network_scrape.pipelines.OtodomDetailsPipeline': 300,
#         },
#         'CONCURRENT_REQUESTS': 16,  # Zwiększenie liczby równoległych żądań
#         'DOWNLOAD_DELAY': 1,  # Ustawienie opóźnienia między żądaniami
#     }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Filtruj ogłoszenia, które mają puste pole z linkami do zdjęć lub tytułem
#         self.ads = list(ListingOtodom.objects.filter( Q(isActive=True)&(
#             Q(original_image_urls__isnull=True) | Q(original_image_urls='[]') | Q(original_image_urls='') | Q(title__isnull=True) | Q(title=''))
#         ).order_by('id'))
#         # self.logger.info(f"Found {len(self.ads)} ads to process.")
#         # for ad in self.ads:
#         #     self.logger.info(f"Ad URL: {ad.url}")

#     def start_requests(self):
#         if not self.ads:
#             self.logger.info("No ads to process.")
#             return

#         for ad in self.ads:
#             self.logger.info(f"Processing ad: {ad.url}")
#             yield Request(url=ad.url, callback=self.parse, meta={'id': ad.id}, errback=self.handle_error)

#     def handle_error(self, failure):
#         self.logger.error(repr(failure))
#         if failure.check(HttpError):
#             response = failure.value.response
#             if response.status == 410:
#                 ad_id = response.meta.get('id')
#                 item = {'id': ad_id, 'isActive': False}
#                 yield item

#     def parse(self, response):
#         ad_id = response.meta['id']
#         try:
#             ad_data = response.json()
#         except json.JSONDecodeError:
#             self.logger.error(f"Response is not JSON for ad id {ad_id}, parsing as HTML")
#             ad_data = self.parse_html(response)

#         if ad_data:
#             ad_data['id'] = ad_id
#             self.logger.info(f"Extracted data for ad id {ad_id}: {ad_data}")
#             yield ad_data
#         else:
#             self.logger.error(f"Failed to extract data for ad id {ad_id}")

#     def parse_html(self, response):
#         ad_data = {}
#         try:
#             # Informacje główne
#             ad_data['title'] = response.css('[data-cy="adPageAdTitle"]::text').get().strip()
#             ad_data['price'] = response.css('[data-cy="adPageHeaderPrice"]::text').get().strip()
#             ad_data['description'] = response.css('[data-cy="adPageAdDescription"] *::text').getall()
#             ad_data['description'] = ' '.join(ad_data['description']).strip()
#             ad_data['address'] = response.css('a[aria-label="Adres"]::text').getall()
#             ad_data['address'] = ''.join(ad_data['address']).strip()
#             ad_data['price_per_m2'] = response.css('[aria-label="Cena za metr kwadratowy"]::text').getall()
#             ad_data['price_per_m2'] = ''.join(ad_data['price_per_m2']).strip()

#             # Znalezienie skryptu zawierającego JSON
#             script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
#             if script:
#                 json_data = json.loads(script)
#                 image_urls = []
#                 # Przeszukiwanie JSON w poszukiwaniu URL-i obrazów
#                 if 'props' in json_data and 'pageProps' in json_data['props']:
#                     ad_info = json_data['props']['pageProps'].get('ad', {})
#                     images = ad_info.get('images', [])
#                     for image in images:
#                         image_url = image.get('large')  # Pobierz URL dużego obrazka
#                         if image_url:
#                             image_urls.append(image_url)
#                 ad_data['original_image_urls'] = image_urls  # Zapisanie URL-i obrazów

#             # self.logger.info(f"Image URLs: {image_urls}")

#             # Pobieranie danych z tabeli "Szczegóły ogłoszenia"
#             features = {}
#             table_rows = response.css('div[data-cy="ad.top-information.table"] div[role="region"]')
#             for row in table_rows:
#                 key = row.css('div[data-cy="table-label-content"]::text').get()
#                 value = row.css('div.css-1wi2w6s::text, a[data-cy="ad-information-link"]::text').get()
#                 if key and value:
#                     features[key.strip()] = value.strip()

#             # tabela Szczegóły ogłoszenia
#             ad_data['square_footage'] = features.get('Powierzchnia')
#             ad_data['rooms'] = features.get('Liczba pokoi')
#             ad_data['floor'] = features.get('Piętro')
#             ad_data['rent'] = features.get('Czynsz')
#             ad_data['remote_service'] = features.get('Obsługa zdalna')
#             ad_data['ownership_form'] = features.get('Forma własności')
#             ad_data['estate_condition'] = features.get('Stan wykończenia')
#             ad_data['balcony'] = features.get('Balkon / ogród / taras')
#             ad_data['parking_space'] = features.get('Miejsce parkingowe')
#             ad_data['heating_type'] = features.get('Ogrzewanie')
#             ad_data['land_area'] = features.get('Powierzchnia działki')
#             ad_data['building_type'] = features.get('Rodzaj zabudowy')
#             ad_data['energy_certificate'] = features.get('Certyfikat energetyczny')
#             ad_data['location'] = features.get('Położenie')
#             ad_data['plot_type'] = features.get('Typ działki')
#             ad_data['dimensions'] = features.get('Wymiary')
#             ad_data['premises_location'] = features.get('Umiejscowienie lokalu')
#             ad_data['purpose'] = features.get('Przeznaczenie')
#             ad_data['construction'] = features.get('Konstrukcja')
#             ad_data['height'] = features.get('Wysokość')
#             ad_data['lighting'] = features.get('Oświetlenie')

#             # Pobieranie danych z tabeli "Informacje dodatkowe"
#             additional_features = {}
#             additional_rows = response.css('div[data-cy="ad.additional-information.table"] div[role="region"]')
#             for row in additional_rows:
#                 key = row.css('div[data-cy="table-label-content"]::text').get()
#                 value = row.css('div.css-1wi2w6s::text, div.css-1wnyucs::text').get()
#                 if key and value:
#                     additional_features[key.strip()] = value.strip()

#             # tabela Informacje dodatkowe
#             ad_data['market_type'] = additional_features.get('Rynek')
#             ad_data['advertiser_type'] = additional_features.get('Typ ogłoszeniodawcy')
#             ad_data['available_from'] = additional_features.get('Dostępne od')
#             ad_data['build_year'] = additional_features.get('Rok budowy')
#             ad_data['estate_type'] = additional_features.get('Rodzaj zabudowy')
#             ad_data['windows'] = additional_features.get('Okna')
#             ad_data['elevator'] = additional_features.get('Winda')
#             ad_data['media'] = additional_features.get('Media')
#             ad_data['security'] = additional_features.get('Zabezpieczenia')
#             ad_data['equipment'] = additional_features.get('Wyposażenie')
#             ad_data['additional_info'] = additional_features.get('Informacje dodatkowe')
#             ad_data['building_material'] = additional_features.get('Materiał budynku')
#             ad_data['location_info'] = additional_features.get('Położenie')
#             ad_data['roof'] = additional_features.get('Dach')
#             ad_data['attic'] = additional_features.get('Poddasze')
#             ad_data['recreational_house'] = additional_features.get('Dom rekreacyjny')
#             ad_data['roof_covering'] = additional_features.get('Pokrycie dachu')
#             ad_data['fencing'] = additional_features.get('Ogrodzenie')
#             ad_data['access_road'] = additional_features.get('Dojazd')
#             ad_data['neighborhood'] = additional_features.get('Okolica')
#             ad_data['office_rooms'] = additional_features.get('Pomieszczenia biurowe')
#             ad_data['social_facilities'] = additional_features.get('Zaplecze socjalne')
#             ad_data['parking'] = additional_features.get('Parking')
#             ad_data['ramp'] = additional_features.get('Rampa')
#             ad_data['floor_material'] = additional_features.get('Posadzka')

#             # Advertiser info
#             ad_data['advertiser_name'] = additional_features.get('Nazwa ogłoszeniodawcy')
#             ad_data['advertiser_phone'] = additional_features.get('Telefon ogłoszeniodawcy')

#             # self.logger.info(f"Parsed HTML data for ad: {ad_data}")

#         except Exception as e:
#             self.logger.error(f"Error parsing HTML: {e}")

#         return ad_data
