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
class brinkborghSpider(scrapy.Spider):
    name = 'brinkborgh'
    start_urls = ['https://www.brinkborgh.nl/wonen/zoeken/heel-nederland/huur/']
    base_url='https://www.brinkborgh.nl'
    handle_httpstatus_list = [404]
    def parse(self, response):
        # Extract item URLs on the current page
        links=response.css('a.card-property::attr(href)').getall()
        items_lenght=len(links)
        status=response.css('body > div.wrapper > main > section > div > div:nth-child(2) > div > div.row > div > a > div.card-property__image > div::text').getall()
        rented=0
        for state in status:
            if normalizeRentstatus(state)=='rented':
                rented=rented+1
        if items_lenght==rented:raise CloseSpider('All items on the page are rented.')
        for i in range(len(links)):
            listing_url =  links[i]
            if normalizeRentstatus(status[i])=='available':
                yield response.follow(
                    url=listing_url, 
                    callback=self.parse_object,
                )
        next_page_url=response.css('a.next.page-numbers::attr(href)').get()
        print(self.base_url+next_page_url)
        if next_page_url:
            yield scrapy.Request(
                url=self.base_url+next_page_url,
                callback=self.parse
            )

    def parse_object(self, response):
        # create new RentalItem which will saved to json file
        item = RentalItem()
        
        item['url'] = response.url
        item['id'] = response.url
        item['status'] = 'available'
        item['title']=response.css('div.house-info__content h1::text').get().strip()
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['livingsurface'] = response.xpath("//strong[text()='Woonoppervlakte']/following-sibling::span/text()").get()
        if item['livingsurface']:item['livingsurface']=int(item['livingsurface'].split()[1].strip())
        item['propertytype'] = response.xpath("//strong[text()='Soort bouw']/following-sibling::span/text()").get()
        if item['propertytype']:item['propertytype']=item['propertytype'].strip()
        city =  converter.handle(response.css("div.house-info__subtitle").get()).split()[-1]
        item['city'] = city.strip()
        item['zipcode']=response.css('div.house-info__subtitle span::text').get().replace(' ','')
        item['rooms'] = response.xpath("//strong[text()='Aantal kamers']/following-sibling::span/text()").get()
        if item['rooms']: item['rooms']=int(item['rooms'].strip())
        item['bedrooms'] = response.xpath("//strong[text()='Aantal slaapkamers']/following-sibling::span/text()").get()
        if item['bedrooms']: item['bedrooms']=int(item['bedrooms'].strip())
        item['bathrooms'] = response.xpath("//strong[text()='Aantal badkamers']/following-sibling::span/text()").get()
        if item['bathrooms']: item['bathrooms']=int(item['bathrooms'].strip())
        item['totalfloors'] = response.xpath("//strong[text()='Aantal woonlagen']/following-sibling::span/text()").get()
        if item['totalfloors']: item['totalfloors']=int(item['totalfloors'].strip())
        price=response.xpath("//strong[text()='Vraagprijs']/following-sibling::span/text()").get()
        if price:
            item['price']=int(price.strip().split()[1].replace('.',''))
        else:
            item['price']=None
        description=''
        for desc in response.css('div.house-description__intro p::text').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        photos=[]
        for photo in response.xpath("//section[@id='media']//a[@class='js-popup-gallery']//img/@data-src").getall():
            photos.append(self.base_url+photo)
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
        item['furnishedstate']=response.xpath("//strong[text()='Bijzonderheden']/following-sibling::span/text()").get()
        item['countryid']=1
        yield item

if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'brinkborgh.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(brinkborghSpider)
    process.start()