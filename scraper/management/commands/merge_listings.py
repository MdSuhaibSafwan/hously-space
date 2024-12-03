from django.core.management.base import BaseCommand
from scraper.models import ListingOtodom, NonlineListings, NetworkMonitoringAdvertisments
from scraper.api.advertisments.merge_listings import merge_listings_to_network_monitoring  # Zakładając, że funkcja znajduje się tutaj

class Command(BaseCommand):
    help = 'Merges listings from ListingOtodom and NonlineListings into NetworkMonitoringAdvertisments'

    def handle(self, *args, **options):
        merge_listings_to_network_monitoring()
        self.stdout.write(self.style.SUCCESS('Successfully merged the listings.'))
