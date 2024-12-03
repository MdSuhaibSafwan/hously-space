from django.db import models

class NonlineListings(models.Model):
    url = models.URLField(max_length=2000, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    isActive = models.BooleanField(default=True)
    inactive_date = models.DateTimeField(null=True, blank=True)
    
    # Informacje główne
    title = models.CharField(max_length=500, null=True, blank=True)
    price = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    price_per_m2 = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=20000, null=True, blank=True)

    # tabela Szczegóły ogłoszenia
    square_footage = models.CharField(max_length=200, null=True, blank=True)
    rooms = models.CharField(max_length=200, null=True, blank=True)
    floor = models.CharField(max_length=200, null=True, blank=True)
    rent = models.CharField(max_length=255, blank=True, null=True)
    remote_service = models.CharField(max_length=255, null=True, blank=True)
    ownership_form = models.CharField(max_length=200, null=True, blank=True)
    estate_condition = models.CharField(max_length=255, null=True, blank=True)
    balcony = models.CharField(max_length=255, null=True, blank=True)
    parking_space = models.CharField(max_length=200, null=True, blank=True)
    heating_type = models.CharField(max_length=200, null=True, blank=True)
    # Dla domów
    land_area = models.CharField(max_length=200, null=True, blank=True)
    building_type = models.CharField(max_length=200, null=True, blank=True)  # Rodzaj zabudowy
    energy_certificate = models.CharField(max_length=200, null=True, blank=True)
    # Dla działek
    location = models.CharField(max_length=200, null=True, blank=True)
    plot_type = models.CharField(max_length=200, null=True, blank=True)
    dimensions = models.CharField(max_length=200, null=True, blank=True)
    # Dla lokali użytkowych
    premises_location = models.CharField(max_length=200, null=True, blank=True)
    purpose = models.CharField(max_length=200, null=True, blank=True)
    # Dla hal i magazynów
    construction = models.CharField(max_length=200, null=True, blank=True)
    height = models.CharField(max_length=200, null=True, blank=True)
    # Dla garaży
    lighting = models.CharField(max_length=200, null=True, blank=True)

    # tabela Informacje dodatkowe
    market_type = models.CharField(max_length=200, null=True, blank=True)
    advertiser_type = models.CharField(max_length=200, null=True, blank=True)
    available_from = models.CharField(max_length=200, null=True, blank=True)
    build_year = models.CharField(max_length=200, null=True, blank=True)
    estate_type = models.CharField(max_length=255, blank=True, null=True)
    windows = models.CharField(max_length=200, null=True, blank=True)
    elevator = models.CharField(max_length=200, null=True, blank=True)
    media = models.CharField(max_length=500, null=True, blank=True)
    security = models.CharField(max_length=500, null=True, blank=True)
    equipment = models.CharField(max_length=500, null=True, blank=True)
    additional_info = models.CharField(max_length=255, null=True, blank=True)
    building_material = models.CharField(max_length=200, null=True, blank=True)
    # Dla domów
    location_info = models.CharField(max_length=200, null=True, blank=True)  # Położenie
    roof = models.CharField(max_length=200, null=True, blank=True)
    attic = models.CharField(max_length=200, null=True, blank=True)  # Poddasze
    recreational_house = models.CharField(max_length=200, null=True, blank=True)
    roof_covering = models.CharField(max_length=200, null=True, blank=True)
    # Dla działek
    fencing = models.CharField(max_length=200, null=True, blank=True)
    access_road = models.CharField(max_length=200, null=True, blank=True)
    neighborhood = models.CharField(max_length=200, null=True, blank=True)  # Okolica
    # Dla hal i magazynów
    office_rooms = models.CharField(max_length=200, null=True, blank=True)
    social_facilities = models.CharField(max_length=200, null=True, blank=True)
    parking = models.CharField(max_length=200, null=True, blank=True)
    ramp = models.CharField(max_length=200, null=True, blank=True)
    floor_material = models.CharField(max_length=200, null=True, blank=True)  # Posadzka

    # Advertiser info
    advertiser_name = models.CharField(max_length=255, null=True, blank=True)
    advertiser_phone = models.CharField(max_length=200, null=True, blank=True)

    # inne
    land_and_mortgage_register = models.CharField(max_length=255, blank=True, null=True)
    listing_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=200, blank=True, null=True)
    view_count = models.CharField(max_length=255, blank=True, null=True)

    # Obrazy
    original_image_urls = models.JSONField(null=True, blank=True)  # Przechowuje listę oryginalnych URL-i obrazów
    images = models.JSONField(null=True, blank=True)  # Przechowuje listę ścieżek do pobranych obrazów

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
