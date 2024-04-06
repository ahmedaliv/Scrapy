import json
import re
import os
import scrapy
import time
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.http import HtmlResponse
from renthousescraper.items import RentalItem
import html2text
from renthousescraper.spiders.globalfunctions import *
converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True  
class geldhofSpider(scrapy.Spider):
    name = 'geldhof'
    start_urls = ['https://www.geldhof.nl/aanbod/woningaanbod/huur/']
    def parse(self, response):
            for item in response.css('div.vakfoto > a::attr(href)').getall():
                listing_url = 'https://www.geldhof.nl' + item
                yield scrapy.Request(
                    url=listing_url, 
                    callback=self.parse_object,
                )
            next_page_url = response.xpath("(//span[contains(@class,'next-page')])[1][a]/@href").get()
            if next_page_url:
                yield scrapy.Request(
                    url='https://www.geldhof.nl'+next_page_url,
                    callback=self.parse,
                )

    def parse_object(self, response):
        # create new RentalItem which will saved to json file
        item = RentalItem()
        item['url'] = response.url
        item['id'] = response.url
        item['status'] = response.css('span.transactiestatus  span.kenmerkValue::text').get().strip()
        item['status']=normalizeRentstatus(item['status'])
        item['title']=response.css('h1.street-address::text').get().strip()
        if item['status'].strip() =='rented':
            return
        item['livingsurface'] = response.xpath("(//span[contains(@class,'woonoppervlakte')])[2]/span[2]/text()").get()
        if item['livingsurface']:item['livingsurface']=int(item['livingsurface'].replace('m²','').strip())
        item['totalvolume']=response.xpath("(//span[contains(@class,'inhoud')])/span[2]/text()").get()
        if item['totalvolume']:item['totalvolume']=int(item['totalvolume'].replace('m³','').strip())
        item['propertytype'] = response.xpath("(//span[contains(@class,'soortobject')])[1]/span[2]/text()").get()
        if item['propertytype']:item['propertytype']=item['propertytype'].strip()
        item['city'] = response.xpath("(//span[contains(@class,'zipcity')])[1]/span[2]/text()").get()
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['zipcode']=response.xpath("(//span[contains(@class,'zipcity')])[1]/span[1]/text()").get().replace(' ','')
        item['rooms'] = response.xpath("(//span[contains(@class,'aantalkamers')])[2]/span[2]/text()").get()
        if item['rooms']: item['rooms']=int(item['rooms'].strip())
        item['bathrooms'] = response.xpath("(//span[contains(@class,'aantalbadkamers')])/span[2]/text()").get()
        if item['bathrooms']: item['bathrooms']=int(item['bathrooms'].strip())
        item['bedrooms'] = response.xpath("(//span[contains(@class,'aantalslaapkamers')])/span[2]/text()").get()
        if item['bedrooms']: item['bedrooms']=int(item['bedrooms'].strip())
        item['totalfloors'] = response.xpath("(//span[contains(@class,'aantalslaapkamers')])/span[2]/text()").get()
        if item['totalfloors']: item['totalfloors']=int(item['totalfloors'].replace('woonlaag','').strip())
        price=response.css('span.huurprijs span.kenmerkValue::text').get()
        if price:
            item['price']=int(price.replace('€','').replace(',-','').replace('.','').replace(' per maand','').strip())
        else:
            item['price']=None
        deposit=response.css('span.waarborgsom span.kenmerkValue::text').get()
        if deposit:
            item['deposit']=int(deposit.replace('€','').replace(',-','').replace('.','').strip())
        else:
            item['deposit']=None
        service=response.css('span.servicekosten span.kenmerkValue::text').get()
        if service:
            item['servicecosts']=int(deposit.replace('€','').replace(',-','').replace('.','').strip())
        else:
            item['servicecosts']=None
        item['description'] =converter.handle(response.css('div#Omschrijving').get()).replace('### Omschrijving','').split('\n\\--')[0].strip()
        photos=[]
        for photo in response.css('div.ogFotos span.fotolist  a::attr(href)').getall():
            photos.append(photo)
        item['construction_year']=response.css('span.bouwjaar span.kenmerkValue::text').get()
        if item['construction_year']:item['construction_year']=int(item['construction_year'].strip())
        item['construction_type']=response.css('span.bouwvorm span.kenmerkValue::text').get().strip()
        item['energylabel']=response.xpath("(//span[contains(@class,'energieklasse')])/span[2]/text()").get()
        if item['energylabel']:item['energylabel']=item['energylabel'].strip()
        parking=response.xpath("(//span[contains(@class,'parkeerfaciliteit')])/span[2]/text()").get()
        if parking:parking=1
        else:parking=0
        item['parking']=parking
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
        item['countryid']=1
        yield item

# if __name__ == "__main__":
#     Settings = {
#         # Specify the output location and format
#         'FEEDS': {os.path.join('result folder', 'geldhof.json'): {
#             'format': 'json',
#         }},

#         # Define user agent to simulate a web browser
#         'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#     }

#     # Create a Scrapy CrawlerProcess with specified settings
#     process = CrawlerProcess(Settings)

#     # Start crawling using the defined spider
#     process.crawl(geldhofSpider)
#     process.start()