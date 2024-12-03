import scrapy
from network_scrape.items import OtodomItem

class OtodomMieszkaniaSpider(scrapy.Spider):
    name = 'otodom_mieszkania'
    allowed_domains = ['otodom.pl']
    start_urls = ['https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie?limit=72']
    max_pages = 4500  # Ograniczenie liczby stron do przeszukania

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'ROBOTSTXT_OBEY': True,
        'ITEM_PIPELINES': {
            'network_scrape.pipelines.OtodomUrlsPipeline': 300,
        },
        'CONCURRENT_REQUESTS': 16,  # Zwiększenie liczby równoległych żądań
        'DOWNLOAD_DELAY': 1.5,  # Ustawienie opóźnienia między żądaniami
    }

    def __init__(self, *args, **kwargs):
        super(OtodomMieszkaniaSpider, self).__init__(*args, **kwargs)
        self.existing_count = 0
        self.links_scraped = 0  # Dodanie zmiennej do przechowywania liczby pobranych linków

    def parse(self, response):
        no_offers_message = response.css('div.css-y6l269.e1ws6l2x2 h3.css-1nw1os0.e1ws6l2x3::text').get()
        if no_offers_message and "Nie znaleźliśmy żadnych ogłoszeń" in no_offers_message:
            self.logger.info("No offers found. Closing spider.")
            self.crawler.engine.close_spider(self, 'no_offers_found')
            return

        articles = response.css('article')  
        if not articles:
            self.logger.warning("No articles found on page.")
        
        for article in articles:
            link = article.css('a::attr(href)').get()  
            if link:
                item = OtodomItem()
                item['url'] = response.urljoin(link)
                self.links_scraped += 1  # Zwiększenie licznika pobranych linków
                yield item

        self.logger.info(f"Number of links scraped: {self.links_scraped}")  # Logowanie liczby pobranych linków

        current_page = response.meta.get('page', 1)
        if current_page >= self.max_pages:
            self.logger.info(f"Reached the limit of {self.max_pages} pages. Closing spider.")
            self.crawler.engine.close_spider(self, 'page_limit_reached')
            return

        next_page = current_page + 1
        next_page_url = f"https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie?limit=72&page={next_page}"
        self.logger.debug(f"Following next page: {next_page_url}")  # Zmniejszenie poziomu logowania
        yield scrapy.Request(next_page_url, callback=self.parse, meta={'page': next_page})

    def process_item(self, item, spider):
        if not item['exists_in_database']:
            self.existing_count = 0  
        else:
            self.existing_count += 1
            if self.existing_count >= 10:
                self.logger.info("Reached limit of 10 existing advertisements in a row. Closing spider.")
                spider.crawler.engine.close_spider(spider, 'existing_limit_reached')

        return item
