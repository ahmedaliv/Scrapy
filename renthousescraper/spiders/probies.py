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
class ExampleSpider(scrapy.Spider):
    name = 'probies'
    start_urls = ['https://www.probies.nl/aanbod/te-huur?start=0']
    def parse(self, response):
            for item in response.css('.title a::attr(href)').getall():
                listing_url = 'https://www.probies.nl' + item
                yield scrapy.Request(
                    url=listing_url, 
                    callback=self.parse_object,
                )
            next_page_url = response.xpath('//a[@title="Volgende"]/@href').get()
            if next_page_url:
                yield scrapy.Request(
                    url='https://www.probies.nl'+next_page_url,
                    callback=self.parse,
                )

    def parse_object(self, response):
        # create new RentalItem which will saved to json file
        item = RentalItem()
        item['url'] = response.url
        item['id'] = response.url
        item['status'] = response.xpath("//td[text()='Huurprijs:']/following-sibling::td[1]/text()").get()
        item['title']=response.css('.title a::text').get().strip()
        if item['status'].strip() =='- verhuurd -':
            return
            item['status'] = 'rented'
            item['price']=None
        else:
            pattern = r'€\s?(\d+(\.\d+)?)'
            item['price']=item['status'].strip()
            match = re.search(pattern, item['price'])
            if match:
                # Extract and return the price
                item['price']= int(match.group(1))
            item['status'] = 'available'
        item['livingsurface'] = response.xpath("//td[text()='Woonoppervlakte:']/following-sibling::td[1]/text()").get()
        if not item['livingsurface']:
            item['livingsurface'] = response.xpath("//td[text()='Oppervlakte:']/following-sibling::td[1]/text()").get()
        item['livingsurface']=int(item['livingsurface'].replace(' m2','').replace(',','').replace('ca. ',''))
        # item['propertytype'] = response.xpath("//td[text()='Type of residence']/following-sibling::td/text()").get()
        # city = response.css("ol.breadcrumb li:nth-of-type(2) a::attr(title)").get()
        # item['city'] = city
        # address = response.xpath("//h1[@class='object_title']/text()").get().strip().replace('For rent: ','')
        # address = address.replace(city,'')       
        # street = address.split(',')[0].strip()
        # item['street'], item['streetnr'] = ''
        # item['zipcode'] = address.split(',')[1].strip()
        item['countryid'] = 1
        item['city']=item['title'].split('-')[-1].replace('St.','').strip()
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['street']=item['street'].replace(item['city'],'').strip()
        item['streetnr']=item['streetnr'].replace('-','').strip()
        # rooms = response.xpath("//td[contains(text(), 'Number of rooms')]/following-sibling::td/text()").get()
        # item['rooms'] = rooms.split(' (')[0].strip()
        # bathrooms = response.xpath("//td[contains(text(), 'Number of bathrooms')]/following-sibling::td/text()").get()
        # item['bathrooms'] = bathrooms.split(' (')[0].strip()
        description=''
        for desc in response.xpath('/html/body/div[2]/div[2]/div[2]/div/div/div/div[1]/p/text()').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        photos=[]
        for photo in response.css(".vsig.vsig1_0 a img::attr(src)").getall():
            photos.append('https://www.probies.nl'+photo)
        
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs

        # item['deposit'] = response.xpath("//td[text()='Deposit']/following-sibling::td/text()").re_first(r'€\s*(\d[\d,.]*)')
        # item['construction_year'] = response.xpath("//td[text()='Construction period']/following-sibling::td/text()").get()

        # # Regular expression to extract the latitude and longitude
        # script_content = ''.join(response.xpath('//script[contains(., "OSMMap")]/text()').getall())
        # lat_lng_pattern = re.compile(r'center: \[(\d+\.\d+), (\d+\.\d+)\]')
        # lat_lng_match = lat_lng_pattern.search(script_content)

        # if lat_lng_match:
        #     longitude, latitude = lat_lng_match.groups()
        #     item['lat'] = latitude
        #     item['lon'] = longitude

        yield item

if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'test.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(ExampleSpider)
    process.start()