import scrapy
from scrapy import Request


class DynamicScraper(scrapy.Spider):
    name = "dynamic_scraper"

    def __init__(self, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls if urls else []

    def parse(self, response):
        pass