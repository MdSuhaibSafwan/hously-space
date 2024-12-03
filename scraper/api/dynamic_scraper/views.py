from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from network_scrape.spiders.dobryadress_spider import DobryAdress
from network_scrape.spiders.gethome_spider import GetHomeSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from rest_framework.response import Response
from rest_framework import status
from ...utils import get_dynamic_scraping_from_hously_cloud


@permission_classes([IsAuthenticated, ])
@api_view(http_method_names=["POST", ])
def dynamic_crawl(request):
    process = CrawlerProcess(get_project_settings())
    process.crawl(GetHomeSpider)
    process.start()

    return Response({"message": "crawl started"}, status=status.HTTP_201_CREATED)
