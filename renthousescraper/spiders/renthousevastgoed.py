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
from scrapy.exceptions import CloseSpider
from renthousescraper.spiders.globalfunctions import *
converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True  
class renthousevastgoedSpider(scrapy.Spider):
    name = 'renthousevastgoed'
    start_urls = ['https://renthousevastgoed.nl/aanbod/']
    current_page = 1
    total_pages = None

    def parse(self, response):
        # Extracting total pages from script
        script = response.xpath('//script[contains(., "FWP_JSON")]/text()').get()
        json_match = re.search(r'window\.FWP_JSON = (.*?});', script)
        if json_match:
            json_data = json_match.group(1)
            data = json.loads(json_data)
            self.total_pages = data.get('preload_data', {}).get('settings', {}).get('pager', {}).get('total_pages')

        # Start with the first page
        if self.total_pages:
            yield scrapy.Request(
                url=f'https://renthousevastgoed.nl/aanbod/?_paged={self.current_page}',
                callback=self.parse_page
            )
    def parse_page(self, response):
        # Extract item URLs on the current page
        links=response.css('.object-image a::attr(href)').getall()
        items_lenght=len(links)
        status=status=response.css('div.object-status::text').getall()
        rented=0
        for state in status:
            if state.strip()=='Verhuurd':
                rented=rented+1
        if items_lenght==rented:raise CloseSpider('All items on the page are rented.')
        for i in range(len(links)):
            listing_url =  links[i]
            yield response.follow(
                url=listing_url, 
                callback=self.parse_object,
            )
        self.current_page += 1
        if self.current_page <= self.total_pages:
            next_page_url = f'https://renthousevastgoed.nl/aanbod/?_paged={self.current_page}'
            yield scrapy.Request(next_page_url, callback=self.parse_page)
        else:
            # No more pages to scrape
            self.log('No more pages to visit.')

    def parse_object(self, response):
        # create new RentalItem which will saved to json file
        item = RentalItem()
        
        item['url'] = response.url
        item['id'] = response.url
        status = response.css("div.object-feature-status div.object-feature-info::text").get().strip()
        item['status']=normalizeRentstatus(status)
        if item['status']=='rented':return
        item['title']=converter.handle(response.css('h1 span.object-address-line:first-child').get()).strip()
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['livingsurface'] = response.css("div.object-feature-woonoppervlakte div.object-feature-info::text").get()
        if item['livingsurface']:item['livingsurface']=int(item['livingsurface'].strip().replace(' m²',''))
        item['totalvolume'] = response.css("div.object-feature-inhoud div.object-feature-info::text").get()
        if item['totalvolume']:item['totalvolume']=int(item['totalvolume'].strip().replace(' m³',''))
        item['propertytype'] = response.css("div.object-feature-woonhuissoort div.object-feature-info::text").get()
        if item['propertytype']:item['propertytype']=item['propertytype'].strip()
        city =  response.css("h1 span.object-address-line:last-child span.object-place::text").get()
        item['city'] = city.strip()
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        #item['street'], item['streetnr'] =(' '.join(item['title'].split(' ')[:-1])).strip(),item['title'].split(' ')[-1]
        item['zipcode']=response.css('h1 span.object-address-line:last-child span.object-zipcode::text').get().replace(' ','')
        rooms=response.css("div.object-feature-aantalkamers div.object-feature-info::text").get()
        item['rooms'] = response.css("div.object-feature-aantalkamers div.object-feature-info::text").get()
        if item['rooms']: item['rooms']=int(item['rooms'].strip().split()[0])
        if rooms:
            match = re.search(r'(\d+)\s*slaapkamers', rooms.strip())
            if match:
                # Extract and return the number of bedrooms
                item['bedrooms']= int(match.group(1))
        item['bathrooms'] = response.css("div.object-feature-aantalbadkamers div.object-feature-info::text").get()
        if item['bathrooms']: item['bathrooms']=int(item['bathrooms'].strip().split()[0])
        item['totalfloors'] = response.css("div.object-feature-aantaletages div.object-feature-info::text").get()
        if item['totalfloors']: item['totalfloors']=int(item['totalfloors'].strip())
        price=response.css('div.object-price-rent span::text').get()
        if price:
            item['price']=price.strip().split()[-1].replace('.','')
        else:
            item['price']=None
        description=''
        for desc in response.css('div.object-detail-description p::text').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        photos=[]
        for photo in response.css('div.object-detail-photos-all img::attr(data-src)').getall():
            photos.append(photo)
        
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
        if not item['photos']:
            photos=[]
            for photo in response.css('div.object-detail-photos-item img::attr(data-src)').getall():
                photos.append(photo)
            
            item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs   
        item['construction_type'] = response.css("div.object-feature-bouwvorm div.object-feature-info::text").get()
        if item['construction_type']:item['construction_type'] =item['construction_type'].strip()
        item['availablefromdate']=response.css('div.object-feature-aanvaarding div.object-feature-info::text').get()
        if item['availablefromdate']:
            item['availablefromdate']=item['availablefromdate'].strip().replace('Beschikbaar per ','')
        # Regular expression to extract the latitude and longitude
        item['parking']=int('Parkeergelegenheid' in converter.handle(response.text))
        item['countryid']=1
        yield item

if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'renthousevastgoed.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(renthousevastgoedSpider)
    process.start()