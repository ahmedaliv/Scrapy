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
class JlgrealestateSpider(scrapy.Spider):
    name = 'jlgrealestate'
    start_urls = ['https://jlgrealestate.com/woningen/huur/']
    def parse(self, response):
            links=response.css('#entity-items a::attr(href)').getall()
            for i in range(len(links)):
                listing_url =  links[i]
                status=response.css(f'#entity-items > article:nth-child({i+1}) > div > figure > span::text').get()
                if status:
                    status=normalizeRentstatus(status)
                    if status!='available':continue
                yield scrapy.Request(
                    url=listing_url, 
                    callback=self.parse_object,
                )
            next_page_url = response.css('div.pagination a::attr(href)').get()
            if next_page_url:
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                )

    def parse_object(self, response):
        # create new RentalItem which will saved to json file
        item = RentalItem()
        item['url'] = response.url
        item['id'] = response.url
        status = response.xpath("//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Status')]/../text()").get()
        item['status']=normalizeRentstatus(status)
        item['title']=response.css('div.woning__header h1::text').get().strip()
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['livingsurface'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Woonoppervlakte')])[1]/../text()").get()
        if item['livingsurface']:item['livingsurface']=int(item['livingsurface'])
        item['propertytype'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Soort object')])[1]/../text()").get()
        address=response.css('div.woning__adres p::text').get()
        city =  address.split()[-1]
        item['city'] = city
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        #item['street'], item['streetnr'] =(' '.join(item['title'].split(' ')[:-1])).strip(),item['title'].split(' ')[-1]
        item['zipcode']=address.split()[0]+address.split()[1].replace(',','')
        item['rooms'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Aantal kamers')])[1]/../text()").get()
        if item['rooms']: item['rooms']=int(item['rooms'])
        item['bedrooms']=response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Aantal slaapkamers')])[1]/../text()").get()
        if item['bedrooms']: item['bedrooms']=int(item['bedrooms'])
        item['bathrooms'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Aantal badkamers')])[1]/../text()").get()
        if item['bathrooms']: item['bathrooms']=int(item['bathrooms'])
        price=response.css('div.woning__prijs p::text').get()
        if price:
            item['price']=price.split()[1].replace(',-','').replace(',','').replace('.','')
        else:
            item['price']=None
        description=''
        for desc in response.css('div.woning__content div.prose.clean p::text').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        photos=[]
        for photo in response.css("div.woning__gallery figure a::attr(href)").getall():
            photos.append(photo)
        
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
        item['construction_year'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Bouwjaar')])[1]/../text()").get()
        if item['construction_year']:item['construction_year']=int(item['construction_year'])
        item['construction_type'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Bouwvorm')])[1]/../text()").get()
        item['totalfloors'] = response.xpath("(//ul[@class='woning__kenmerken__list']/li/span[contains(text(),'Aantal woonlagen')])[1]/../text()").get()
        if item['totalfloors']:item['totalfloors']=int(item['totalfloors'])
        item['availablefromdate']=response.css('ul > li:nth-child(5) > span.woning__feature__text > font > font::text').get()
        if not item['availablefromdate']:
            item['availablefromdate']=None
        # Regular expression to extract the latitude and longitude
        item['parking']=int('Parking' in converter.handle(response.text))
        item['countryid']=1
        yield item

# if __name__ == "__main__":
#     Settings = {
#         # Specify the output location and format
#         'FEEDS': {os.path.join('result folder', 'jlgrealestate.json'): {
#             'format': 'json',
#         }},

#         # Define user agent to simulate a web browser
#         'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#     }

#     # Create a Scrapy CrawlerProcess with specified settings
#     process = CrawlerProcess(Settings)

#     # Start crawling using the defined spider
#     process.crawl(JlgrealestateSpider)
#     process.start()