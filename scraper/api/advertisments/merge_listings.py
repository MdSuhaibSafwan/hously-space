from django.db import transaction
from scraper.api.otodom.models_otodom_listings import ListingOtodom
from scraper.api.nonline.models_nonline_listings import NonlineListings
from scraper.api.advertisments.models_network_monitoring import NetworkMonitoringAdvertisments

BATCH_SIZE = 1000  # Adjust the batch size based on your memory constraints

def fetch_in_batches(queryset, batch_size=BATCH_SIZE):
    batch_start = 0
    while True:
        batch = list(queryset[batch_start:batch_start + batch_size])
        if not batch:
            break
        yield batch
        batch_start += batch_size

@transaction.atomic
def merge_listings_to_network_monitoring():
    otodom_listings = ListingOtodom.objects.filter(isActive=True)
    nonline_listings = NonlineListings.objects.filter(isActive=True)

    for batch in fetch_in_batches(otodom_listings):
        new_entries = []
        for listing in batch:
            if not NetworkMonitoringAdvertisments.objects.filter(url=listing.url).exists():
                new_entry = NetworkMonitoringAdvertisments(
                    url=listing.url,
                    images=listing.images,
                    title=listing.title,
                    description=listing.description,
                    address=listing.address,
                    price=listing.price,
                    price_per_meter=listing.price_per_m2,
                    currency=listing.currency,
                    rent=listing.rent,
                    remote_service=listing.remote_service,
                    estate_type=listing.estate_type,
                    building_type=listing.building_type,
                    floor=listing.floor,
                    estate_condition=listing.estate_condition,
                    rooms=listing.rooms,
                    square_footage=listing.square_footage,
                    market_type=listing.market_type,
                    phone_number=listing.advertiser_phone,
                    heating_type=listing.heating_type,
                    building_material=listing.building_material,
                    build_year=listing.build_year,
                    balcony=listing.balcony,
                    parking_space=listing.parking_space,
                    land_and_mortgage_register=listing.land_and_mortgage_register,
                    view_count=listing.view_count
                )
                new_entries.append(new_entry)
        NetworkMonitoringAdvertisments.objects.bulk_create(new_entries, ignore_conflicts=True)

    for batch in fetch_in_batches(nonline_listings):
        new_entries = []
        for listing in batch:
            if not NetworkMonitoringAdvertisments.objects.filter(url=listing.url).exists():
                new_entry = NetworkMonitoringAdvertisments(
                    url=listing.url,
                    images=listing.images,
                    title=listing.title,
                    description=listing.description,
                    address=listing.address,
                    price=listing.price,
                    price_per_meter=listing.price_per_m2,
                    currency=listing.currency,
                    rent=listing.rent,
                    remote_service=listing.remote_service,
                    estate_type=listing.estate_type,
                    building_type=listing.building_type,
                    floor=listing.floor,
                    estate_condition=listing.estate_condition,
                    rooms=listing.rooms,
                    square_footage=listing.square_footage,
                    market_type=listing.market_type,
                    phone_number=listing.advertiser_phone,
                    heating_type=listing.heating_type,
                    building_material=listing.building_material,
                    build_year=listing.build_year,
                    balcony=listing.balcony,
                    parking_space=listing.parking_space,
                    land_and_mortgage_register=listing.land_and_mortgage_register,
                    view_count=listing.view_count
                )
                new_entries.append(new_entry)
        NetworkMonitoringAdvertisments.objects.bulk_create(new_entries, ignore_conflicts=True)
