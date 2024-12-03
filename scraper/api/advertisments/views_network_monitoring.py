from rest_framework import viewsets
from scraper.models import NetworkMonitoringAdvertisments
from scraper.api.advertisments.serializers_network_monitoring import NetworkMonitoringSerializer


class NetworkMonitoringViewSet(viewsets.ModelViewSet):
    queryset = NetworkMonitoringAdvertisments.objects.all()
    serializer_class = NetworkMonitoringSerializer
