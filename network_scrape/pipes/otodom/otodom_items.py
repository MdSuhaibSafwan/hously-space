# network_scrape/items.py

from scrapy_djangoitem import DjangoItem
from scraper.models import ListingOtodom
import scrapy

class OtodomItem(DjangoItem):
    django_model = ListingOtodom

    # Informacje główne
    id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    price_per_m2 = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()

    # tabela Szczegóły ogłoszenia
    square_footage = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    rent = scrapy.Field()
    remote_service = scrapy.Field()
    ownership_form = scrapy.Field()
    estate_condition = scrapy.Field()
    balcony = scrapy.Field()
    parking_space = scrapy.Field()
    heating_type = scrapy.Field()
    land_area = scrapy.Field()
    building_type = scrapy.Field()
    energy_certificate = scrapy.Field()
    location = scrapy.Field()
    plot_type = scrapy.Field()
    dimensions = scrapy.Field()
    premises_location = scrapy.Field()
    purpose = scrapy.Field()
    construction = scrapy.Field()
    height = scrapy.Field()
    lighting = scrapy.Field()

    # tabela Informacje dodatkowe
    market_type = scrapy.Field()
    advertiser_type = scrapy.Field()
    available_from = scrapy.Field()
    build_year = scrapy.Field()
    estate_type = scrapy.Field()
    windows = scrapy.Field()
    elevator = scrapy.Field()
    media = scrapy.Field()
    security = scrapy.Field()
    equipment = scrapy.Field()
    additional_info = scrapy.Field()
    building_material = scrapy.Field()
    location_info = scrapy.Field()
    roof = scrapy.Field()
    attic = scrapy.Field()
    recreational_house = scrapy.Field()
    roof_covering = scrapy.Field()
    fencing = scrapy.Field()
    access_road = scrapy.Field()
    neighborhood = scrapy.Field()
    office_rooms = scrapy.Field()
    social_facilities = scrapy.Field()
    parking = scrapy.Field()
    ramp = scrapy.Field()
    floor_material = scrapy.Field()

    # Advertiser info
    advertiser_name = scrapy.Field()
    advertiser_phone = scrapy.Field()
    
    isActive = scrapy.Field()
    inactive_date = scrapy.Field()
    
    #obrazy
    original_image_urls = scrapy.Field()
    images = scrapy.Field()


