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
converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True  
class domicaSpider(scrapy.Spider):
    name = 'domica'
    start_urls = ['https://www.domica.nl/rts/collections/public/3d202c54/runtime/collection/EAZLEE/data?page=%7B%22pageSize%22%3A100%2C%22pageNumber%22%3A0%7D&filters=%7B%22field%22%3A%22division%22%2C%22operator%22%3A%22eq%22%2C%22value%22%3A%22property%22%7D&filters=%7B%22field%22%3A%22tmp_label%22%2C%22operator%22%3A%22NIN%22%2C%22value%22%3A%5B%22*%22%5D%7D&filters=%7B%22field%22%3A%22tmp_forrent%22%2C%22operator%22%3A%22EQ%22%2C%22value%22%3A%221%22%7D&filters=%7B%22field%22%3A%22tmp_city%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_streetAddress%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_property_type_1%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_num_bedrooms%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22tmp_interior%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_surface%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22tmp_price%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22tmp_price%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22po-api%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&language=DUTCH']
    debug = True
    def __init__(self, *args, **kwargs):
        super(domicaSpider, self).__init__(*args, **kwargs)
        output_file_path = 'C:/scrapy/domica.json'  # Define the output file path
        # Check if the file exists and clear it
        if os.path.exists(output_file_path):
            open(output_file_path, 'w').close()
    def parse(self, response):
            item = RentalItem()
            json_response = json.loads(response.text)
            items=json_response['values']
            for it in items:
                status=normalizeRentstatus(it['data']['tmp_label'])
                if status=='available':
                    item = RentalItem()
                    item['url'] ='https://www.domica.nl/woning/'+ it['data']['url']
                    item['id'] = it['data']['id']
                    item['status'] = 'available' # we only visit the available items
                    item['title']=it['data']['tmp_streetAddress']
                    # item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
                    item['livingsurface'] = it['data']['surface']
                    if not item['livingsurface']:item['livingsurface']=None
                    item['totalvolume'] = it['data']['area_totals']['volume_total']
                    if not item['totalvolume']:item['totalvolume']=None
                    if item['livingsurface']:it['livingsurface']=int(item['livingsurface'])
                    item['propertytype'] = it['data']['property_type']['property_type_1']
                    item['description']=converter.handle(it['data']['description'])
                    city =  it['data']['locality']['city']
                    item['city'] = city
                    item['street'], it['streetnr'] = it['data']['locality']['street'],it['data']['locality']['number']
                    item['zipcode']=it['data']['locality']['zipcode']
                    item['rooms'] = it['data']['counts']['total_rooms']
                    bedrooms= it['data']['counts']['num_bedrooms']
                    if bedrooms:
                        item['bedrooms'] =bedrooms
                    else:item['bedrooms']=None
                    bathrooms = it['data']['counts']['num_bathrooms']
                    if bathrooms:
                        item['bathrooms'] = bathrooms
                    else:item['bathrooms']=None
                    item['totalfloors'] = it['data']['counts']['num_livinglayers']
                    if not item['totalfloors']:item['totalfloors']=None
                    if item['rooms']: item['rooms']=int(item['rooms'])
                    item['price']= it['data']['price']
                    item['deposit']= it['data']['financials']['deposit']
                    item['furnishedstate']=it['data']['tmp_interior']
                    photos=[]
                    for photo in it['data']['photos_middle']:
                        photos.append(photo['url'])
                    if it['data']['parking']['parkings']:
                        item['parking']=1
                    else:
                        item['parking']=0
                    item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
                    item['countryid']=1
                    item['energylabel']=it['data']['climat_control']['energy_label']
                    item['servicecosts']=it['data']['financials']['forsale_service_costs']
                    if item['servicecosts']:item['servicecosts']=float(item['servicecosts'])
                    else:item['servicecosts']=None
                    item['availablefromdate']=it['data']['available_at']
                    item['construction_year']=it['data']['construction']['buildyear']
                    item['lat'] = float(it['data']['locality']['lat'])
                    item['lon'] = float(it['data']['locality']['lng'])
                    yield item
            if json_response['page']['totalItems'] > len(items):
                yield scrapy.Request(
                    url='https://www.domica.nl/rts/collections/public/3d202c54/runtime/collection/EAZLEE/data?page=%7B%22pageSize%22%3A100%2C%22pageNumber%22%3A1%7D&filters=%7B%22field%22%3A%22division%22%2C%22operator%22%3A%22eq%22%2C%22value%22%3A%22property%22%7D&filters=%7B%22field%22%3A%22tmp_label%22%2C%22operator%22%3A%22NIN%22%2C%22value%22%3A%5B%22*%22%5D%7D&filters=%7B%22field%22%3A%22tmp_forrent%22%2C%22operator%22%3A%22EQ%22%2C%22value%22%3A%221%22%7D&filters=%7B%22field%22%3A%22tmp_city%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_streetAddress%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_property_type_1%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_num_bedrooms%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22tmp_interior%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&filters=%7B%22field%22%3A%22tmp_surface%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22tmp_price%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22tmp_price%22%2C%22operator%22%3A%22GTE%22%2C%22value%22%3A%220%22%7D&filters=%7B%22field%22%3A%22po-api%22%2C%22operator%22%3A%22NE%22%2C%22value%22%3A%22*%22%7D&language=DUTCH',
                    callback=self.parse
                    )
if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('C:/scrapy/', 'domica.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(domicaSpider)
    process.start()