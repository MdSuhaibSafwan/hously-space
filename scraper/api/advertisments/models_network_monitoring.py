from django.db import models
from django.contrib.auth.models import User

class NetworkMonitoringAdvertisments(models.Model):
    site_id = models.CharField(max_length=250, blank=True)
    url = models.URLField(max_length=500, unique=True)  # Dodanie pola URL
    images = models.JSONField(default=list, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=7500, blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    
    price = models.CharField(max_length=255, blank=True, null=True)    
    price_per_meter = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)    
    rent = models.CharField(max_length=255, blank=True, null=True)
    
    remote_service = models.CharField(max_length=255, blank=True, null=True)
    estate_type = models.CharField(max_length=255, blank=True, null=True)
    building_type = models.CharField(max_length=255, blank=True, null=True)
    floor = models.CharField(max_length=255, blank=True, null=True)
    estate_condition = models.CharField(max_length=255, blank=True, null=True)
    total_floors = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True)
    rooms = models.CharField(max_length=255, blank=True, null=True)
    bathrooms = models.CharField(max_length=255, blank=True, null=True)
    
    
    square_footage = models.CharField(max_length=255, blank=True, null=True)
    lot_size = models.CharField(max_length=255, blank=True, null=True)
    property_form = models.CharField(max_length=255, blank=True, null=True)
    market_type = models.CharField(max_length=255, blank=True, null=True)
    offer_type = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    
    
    heating_type = models.CharField(max_length=255, blank=True, null=True)
    building_material = models.CharField(max_length=255, blank=True, null=True)
    build_year = models.CharField(max_length=255, blank=True, null=True)
    balcony = models.CharField(max_length=255, blank=True, null=True)
    terrace = models.CharField(max_length=255, blank=True, null=True)
    sauna = models.CharField(max_length=255, blank=True, null=True)
    jacuzzi = models.CharField(max_length=255, blank=True, null=True)
    basement = models.CharField(max_length=255, blank=True, null=True)
    elevator = models.CharField(max_length=255, blank=True, null=True)
    garden = models.CharField(max_length=255, blank=True, null=True)
    air_conditioning = models.CharField(max_length=255, blank=True, null=True)
    
    
    garage = models.CharField(max_length=255, blank=True, null=True)
    parking_space = models.CharField(max_length=255, blank=True, null=True)
    land_and_mortgage_register = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title



