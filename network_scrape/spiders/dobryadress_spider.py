import scrapy
from scrapy import Request


class DobryAdress(scrapy.Spider):
    name = "dobry_adress"

    start_urls = [
        "https://www.dobryadres.pl/lista-ofert.php",
    ]

    def parse(self, response):
        divs = response.css(".lista_ofert")
        lst = divs.css("a::attr(href)").getall()
        new_lst = []
        for i in lst:
            if ".html" in i:
                new_lst.append(i)

        print(lst)
        self.log("List --> ", lst)

        for url in new_lst:
            url = response.urljoin(url)
            yield Request(url, callback=self.parse_each_real_estate_data)

        next_page_div = response.css(".linki_pn")
        if len(next_page_div) != 0:
            next_page_div.reverse()
            next_page_url = next_page_div.attrib["href"]
            next_page_number = int(next_page_url.split("strona=")[-1])
            try:
                curr_page_number = int(response.url.split("strona=")[-1])
            except ValueError as e:
                curr_page_number = 1

            if next_page_number > curr_page_number:
                url = response.urljoin(next_page_url)
                yield Request(url, callback=self.parse)

     
    def parse_each_real_estate_data(self, response):
        self.log(f"URL: {response.url}")
        data = {}
        keys = response.css(".oferta_tabela_50_1::text").getall()
        values = response.css(".oferta_tabela_50_2::text").getall()
        try:
            keys.remove(" ")
        except ValueError:
            pass
        try:
            values.remove(" ")
        except ValueError:
            pass

        num = 0
        if len(keys) > len(values):
            num = len(values)
        else:
            num = len(keys)

        data_dict = {}
        for i in range(num):
            data[keys[i]] = values[i]

        str_lst = []
        desc_response = response.css(".trescmaterialu::text").getall()
        for d in desc_response:
            if (("\n" in d) or ("\t" in d)):
                new_str = "".join(i for i in d.split("\n"))
                new_str = "".join(i for i in new_str.split("\t"))
                new_str = "".join(i for i in new_str.split("\r"))

            str_lst.append(new_str)

        description = "".join(i for i in str_lst)
        data["description"] = description

        image_response = response.css(".oferta_zdjecia").css("img::attr(src)").getall()
        images = []
        for i in image_response:
            images.append(f"{self.start_urls[0]}{i}")

        data["images"] = images

        self.log(data)