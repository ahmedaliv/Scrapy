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
class broersmaSpider(scrapy.Spider):
    name = 'broersma'
    start_urls = ['https://www.broersma.nl/app/uploads/cache/wonen_aanbod_nl.json']
    debug = True
        
    def parse(self, response):
            item = RentalItem()
            json_response = json.loads(response.text)
            items=json_response['objects']
            for it in items:
                if it['status'] == 'Beschikbaar' and it['filters']['type'][0]=='huur':
                    item = RentalItem()
                    item['url'] = it['url']
                    item['id'] = it['id']
                    item['status'] = 'available' # we only visit the available items
                    item['title']=it['title']
                    # item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
                    item['livingsurface'] = it['oppervlakte']
                    if item['livingsurface']:item['livingsurface']=int(item['livingsurface'])
                    item['propertytype'] = it['filters']['collection'][0]
                    city =  it['place']
                    item['city'] = city
                    item['street'], item['streetnr'] = it['street'],it['housenumber']
                    item['zipcode']=it['zipcode']
                    item['rooms'] = it['rooms']
                    if item['rooms']: item['rooms']=int(item['rooms'])
                    item['price']= it['price']
                    if 'Gemeubileerd' in it['specifications']:
                        item['furnishedstate']='furnished'
                    photos=[]
                    for photo in it['gallery']:
                        photos.append(photo)
                    item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
                    item['countryid']=1
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
        description=''
        for desc in response.css('div.read-more--container p ::text').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        yield item
if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'broersma.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(broersmaSpider)
    process.start()