import json
import re
import os
import scrapy
import time
import urllib.request
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import html2text
from renthousescraper.spiders.globalfunctions import *
from renthousescraper.items import RentalItem
class frisiamakelaarsSpider(scrapy.Spider):
    name = 'frisiamakelaars'
    start_urls = ['https://frisiamakelaars.nl/api/properties/available.json']
    debug = True
    def parse(self, response):
            json_response = json.loads(response.text)
            items=json_response['objects']
            
            for it in items:
                if it['availability_status'] == 'beschikbaar' and it['rent_condition']=='per maand':
                    item = RentalItem()
                    item['url'] = it['url']
                    item['id'] = it['object_code']
                    item['status'] = 'available' # we only visit the available items
                    item['title']=it['short_title']
                    item['rooms']=it['filters']['rooms_amount']
                    item['bedrooms']=it['amount_of_bedrooms']
                    item['price']= it['rent_price']
                    item['lat'] = float(it['lat'])
                    item['lon'] = float(it['lng'])
                    yield response.follow(
                    url=item['url'], 
                    callback=self.parse_object,
                    meta={'item':item}
                        )
    def parse_object(self, response):
        # create new RentalItem which will saved to json file
        item = response.meta['item']
        item['livingsurface'] =response.xpath("//span[text()='Woonoppervlakte ']/following-sibling::span/text()").get()
        if item['livingsurface']:item['livingsurface']=int(item['livingsurface'].replace('m²','').strip())
        item['totalvolume']=response.xpath("//span[text()='Inhoud']/following-sibling::span/text()").get()
        if item['totalvolume']:item['totalvolume']=int(item['totalvolume'].replace('m³','').strip())
        item['propertytype'] =response.xpath("//span[text()='Woning type']/following-sibling::span/text()").get()
        if item['propertytype']:item['propertytype']=item['propertytype'].strip()
        address=response.css('h1.section__title span:last-child::text').get().strip()
        city =  address.split()[-1]
        item['city'] = city
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['zipcode']=address.split()[0]+address.split()[1].replace(',','')
        description=''
        for desc in response.css('div.description.description--full p::text').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        photos=[]
        for photo in response.css('div.object-hero__inner figure img::attr(src)').getall():
            photos.append('https://frisiamakelaars.nl'+photo)
        if 'gemeubileerd' in description:
            item['furnishedstate']='furnished'
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
        item['construction_year']=response.xpath("//span[text()='Bouwjaar']/following-sibling::span/text()").get()
        if item['construction_year']:item['construction_year']=int(item['construction_year'])
        item['construction_type']=response.xpath("//span[text()='Bouwvorm']/following-sibling::span/text()").get()
        item['totalfloors']=response.xpath("(//span[text()='Aantal woonlagen']/following-sibling::span)[1]/text()").get()
        if item['totalfloors']:item['totalfloors']=int(item['totalfloors'].strip())
        item['energylabel']=response.xpath("(//span[text()='Energielabel']/following-sibling::span)[1]/text()").get()
        item['countryid']=1
        yield item
# if __name__ == "__main__":
#     Settings = {
#         # Specify the output location and format
#         'FEEDS': {os.path.join('result folder', 'frisiamakelaars.json'): {
#             'format': 'json',
#         }},

#         # Define user agent to simulate a web browser
#         'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#     }

#     # Create a Scrapy CrawlerProcess with specified settings
#     process = CrawlerProcess(Settings)

#     # Start crawling using the defined spider
#     process.crawl(frisiamakelaarsSpider)
#     process.start()