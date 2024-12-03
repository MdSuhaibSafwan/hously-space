
# network_scrape/pipelines.py

from scrapy_djangoitem import DjangoItem
import logging
from asgiref.sync import sync_to_async
import asyncio
from django.db.utils import IntegrityError
from scraper.models import ListingOtodom
import scrapy
from django.apps import apps

class OtodomUrlsPipeline:
    def __init__(self):
        self.existing_count = 0

    async def open_spider(self, spider):
        self.existing_count = 0

    async def close_spider(self, spider):
        pass

    async def process_item(self, item, spider):
        try:
            # Sprawdź, czy URL już istnieje w bazie danych
            ad_exists = await sync_to_async(ListingOtodom.objects.filter(url=item['url']).exists)()
            if not ad_exists:
                ad = ListingOtodom(url=item['url'])  # Tylko URL
                await sync_to_async(ad.save)()
                spider.logger.info(f"Created new advertisement: {item['url']}")  # Logowanie dla nowego ogłoszenia
                self.existing_count = 0  # Zresetuj licznik jeśli ogłoszenie jest nowe
            else:
                spider.logger.info(f"Advertisement already exists: {item['url']}")
                self.existing_count += 1
                if self.existing_count >= 500:
                    spider.logger.info("Reached limit of 500 existing advertisements in a row. Closing spider.")
                    spider.crawler.engine.close_spider(spider, 'existing_limit_reached')
        except IntegrityError as e:
            spider.logger.error(f"IntegrityError for item {item['url']}: {str(e)}")

        return item


from asgiref.sync import sync_to_async
import logging
from scraper.models import ListingOtodom
from datetime import datetime

class OtodomDetailsPipeline:
    async def process_item(self, item, spider):
        if 'id' in item:
            try:
                ad = await sync_to_async(ListingOtodom.objects.get)(id=item['id'])

                # Aktualizuj wszystkie dane, niezależnie od stanu isActive
                ad.title = item.get('title')
                ad.price = item.get('price')
                ad.price_per_m2 = item.get('price_per_m2')
                ad.description = item.get('description')
                ad.address = item.get('address')
                
                # Tabela Szczegóły ogłoszenia
                ad.square_footage = item.get('square_footage')
                ad.rooms = item.get('rooms')
                ad.floor = item.get('floor')
                ad.rent = item.get('rent')
                ad.remote_service = item.get('remote_service')
                ad.ownership_form = item.get('ownership_form')
                ad.estate_condition = item.get('estate_condition')
                ad.balcony = item.get('balcony')
                ad.parking_space = item.get('parking_space')
                ad.heating_type = item.get('heating_type')
                ad.land_area = item.get('land_area')
                ad.building_type = item.get('building_type')
                ad.energy_certificate = item.get('energy_certificate')
                ad.location = item.get('location')
                ad.plot_type = item.get('plot_type')
                ad.dimensions = item.get('dimensions')
                ad.premises_location = item.get('premises_location')
                ad.purpose = item.get('purpose')
                ad.construction = item.get('construction')
                ad.height = item.get('height')
                ad.lighting = item.get('lighting')

                # Tabela Informacje dodatkowe
                ad.market_type = item.get('market_type')
                ad.advertiser_type = item.get('advertiser_type')
                ad.available_from = item.get('available_from')
                ad.build_year = item.get('build_year')
                ad.estate_type = item.get('estate_type')
                ad.windows = item.get('windows')
                ad.elevator = item.get('elevator')
                ad.media = item.get('media')
                ad.security = item.get('security')
                ad.equipment = item.get('equipment')
                ad.additional_info = item.get('additional_info')
                ad.building_material = item.get('building_material')
                ad.location_info = item.get('location_info')
                ad.roof = item.get('roof')
                ad.attic = item.get('attic')
                ad.recreational_house = item.get('recreational_house')
                ad.roof_covering = item.get('roof_covering')
                ad.fencing = item.get('fencing')
                ad.access_road = item.get('access_road')
                ad.neighborhood = item.get('neighborhood')
                ad.office_rooms = item.get('office_rooms')
                ad.social_facilities = item.get('social_facilities')
                ad.parking = item.get('parking')
                ad.ramp = item.get('ramp')
                ad.floor_material = item.get('floor_material')

                # Informacje o ogłoszeniodawcy
                ad.advertiser_name = item.get('advertiser_name')
                ad.advertiser_phone = item.get('advertiser_phone')
                ad.original_image_urls = item.get('original_image_urls', [])

                # Sprawdź i zaktualizuj isActive i inactive_date
                if 'isActive' in item and ad.isActive != item['isActive']:
                    ad.isActive = item['isActive']
                    if not item['isActive']:
                        ad.inactive_date = datetime.now()
                        logging.info(f"Ad id {ad.id} is now inactive.")

                await sync_to_async(ad.save)()
                logging.info(f"Details saved for ad id: {ad.id} with data: {item}")

            except ListingOtodom.DoesNotExist:
                logging.error(f"Advertisement with id {item['id']} does not exist.")
            except Exception as e:
                logging.error(f"Error updating ad id {item['id']}: {e}")
                logging.error(f"Failed item data: {item}")
        return item



from asgiref.sync import sync_to_async
import logging
from scraper.models import ListingOtodom
from datetime import datetime

class OtodomIsActivePipeline:
    async def process_item(self, item, spider):
        if 'isActive' in item and 'id' in item:
            try:
                ad = await sync_to_async(ListingOtodom.objects.get)(id=item['id'])
                if ad.isActive != item['isActive']:  # Loguj tylko, gdy zmienia się wartość isActive
                    ad.isActive = item['isActive']
                    if not item['isActive']:  # Jeśli isActive jest ustawione na False
                        ad.inactive_date = datetime.now()  # Ustaw datę zmiany na False
                        logging.info(f"Ad id {ad.id} is now inactive.")
                    await sync_to_async(ad.save)()
            except ListingOtodom.DoesNotExist:
                logging.error(f"Advertisement with id {item['id']} does not exist.")
            except Exception as e:
                logging.error(f"Error updating isActive status for ad id {item['id']}: {e}")
        return item





import logging
from scraper.models import ListingOtodom
from asgiref.sync import sync_to_async
from django.utils import timezone

class OtodomDownloadImagesPipeline:
    async def process_item(self, item, spider):
        if 'images' in item and 'id' in item:
            try:
                ad = await sync_to_async(ListingOtodom.objects.get)(id=item['id'])
                ad.images = item['images']
                if 'isActive' in item and item['isActive']:
                    ad.isActive = False
                    ad.inactive_date = timezone.now()
                await sync_to_async(ad.save)()
                logging.info(f"Images updated for ad id {ad.id}")
            except ListingOtodom.DoesNotExist:
                logging.error(f"Advertisement with id {item['id']} does not exist.")
            except Exception as e:
                logging.error(f"Error updating images for ad id {item['id']}: {e}")
        return item
