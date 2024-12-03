import scrapy
from scrapy import Request, FormRequest


class GetHomeSpider(scrapy.Spider):
    name = "gethome"

    start_urls = [
        "https://gethome.pl/"
    ]

    traslation_dict = {
        "cena": "price",
        "liczba pokoi": "number of rooms",
        "powierzchnia": "surface",
        "cena za m2": "price per m2",
        "piętro": "floor",
        "dodatkowa pow.": "additional area",
        "liczba pięter": "number of floors",
        "liczba sypialni": "number of bedrooms",
        "ogrzewanie": "heating",
        "liczba balkonów:": "number of balconies",
    }
    # Need to make sure again if translations are right

    def parse(self, response):
        sections = response.css(".gh-1p09fht")
        for div in sections:
            division = div.css("h2.gh-12h4lqq::text").get()
            cities = div.css("ul.gh-2gkv4u li")
            for city in cities:
                url = city.css("a::attr(href)").get()
                url = response.urljoin(url)
                yield Request(url, callback=self.parse_data_of_city_real_estate)
        

    def parse_data_of_city_real_estate(self, response):
        if response.status == 200:
            # print("Getting Response from city: ", response.url)
            urls = response.css("a.o13k6g1y::attr(href)").getall()
            for url in urls:
                url = response.urljoin(url)
                yield Request(url, callback=self.parse_each_apartment_data)

            # real_estate_list = response.css("li.o1iv0nf6")
            # for each_state in real_estate_list:
            #     name = each_state.css("div a.o13k6g1y article h3 div::text").get()
            #     # print("Name: ", name)
            #     address = each_state.css("div a.o13k6g1y article h3 address::text").get()
            #     # print("Address: ", address)
            #     room_number, room_size = each_state.css(".o1byxe3i  .o16iaxib .ngl9ymk::text").getall()
            #     # print("Room size, ", room_size)
            #     # print("Room number: ", room_number)
            #     # print("\n\n")

    def parse_each_apartment_data(self, response):
        name = response.css("header article h1::text").get()
        address = response.css("h2.t129p2ny::text").get()

        div_responses = response.css(".gh-15dfr6w")
        data_dict = {}
        for div in div_responses:
            name = div.css(".gh-1qzesdd::text").get()
            val = div.css(".gh-1johxon::text").get()
            self.add_to_dictionary(name, val, data_dict)
    
        div_responses = response.css(".gh-z6h6j9")
        for div in div_responses:
            name = div.css(".gh-1qpux1j::text").get()
            val = div.css(".gh-tpwp2::text").get()
            self.add_to_dictionary(name, val, data_dict)

        divs = response.css(".gh-1opi3pn")
        for i in divs:
            name = i.css("div p::text").get()
            val = i.css("div p span::text").get() 
            self.add_to_dictionary(name, val, data_dict)

        print(data_dict)

    def add_to_dictionary(self, name, val, data_dict):
        if name is None:
            return

        try:
            data_dict[self.traslation_dict[str(name).lower()]] = val
        except KeyError:
            data_dict[str(name).lower()] = val

        return data_dict