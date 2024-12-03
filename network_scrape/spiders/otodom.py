import scrapy
from scrapy import Request


class DynamicScraper(scrapy.Spider):
    name = "otodom_2"
    start_urls = [
        "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/cala-polska?viewType=listing"
    ]

    def parse(self, response):
        if not (response.status == 200):
            return 
        
        urls = response.css("a::attr(href)").getall()
        

