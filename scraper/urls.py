from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scraper.api.advertisments.views_network_monitoring import NetworkMonitoringViewSet

router = DefaultRouter()
router.register(r'advertisements', NetworkMonitoringViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("crawl/", include("scraper.api.dynamic_scraper.urls")),
]
