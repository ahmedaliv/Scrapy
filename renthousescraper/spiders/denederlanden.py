from renthousescraper.items import RentalItem 
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
from scrapy_splash import SplashRequest
from renthousescraper.spiders.globalfunctions import *
converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True  
class DenNederlandenSpider(scrapy.Spider):
    name = 'denederlanden'
    allowed_domains = ['www.denederlanden.eu']
    start_urls = ['https://www.denederlanden.eu/wonen/zoeken/heel-nederland/huur/']

    def __init__(self, *args, **kwargs):
        super(DenNederlandenSpider, self).__init__(*args, **kwargs)
        self.rented_items_on_page = 0
        self.items_processed = 0

    def parse(self, response):
        self.rented_items_on_page = 0
        self.items_processed = 0
        item_urls = response.css('a.card-property::attr(href)').getall()

        if not item_urls:
            self.logger.info("No items found on this page.")
            return
        
        total_items = len(item_urls)
        for item_url in item_urls:
            yield response.follow(item_url, self.parse_item, meta={'total_items': total_items, 'next_page_url': response.css('a.next.page-numbers::attr(href)').get()})

    def parse_item(self, response):
        self.items_processed += 1
        total_items = response.meta['total_items']
        next_page_url = response.meta['next_page_url']

        status = normalizeRentstatus(response.xpath("//strong[text()='Status:']/following-sibling::span/text()").get())
        if status != 'available':
            self.rented_items_on_page += 1

        if status == 'available':
            item = RentalItem()
            item['url'] = response.url
            item['id'] = response.url
            item['status']=normalizeRentstatus(status)
            item['title']=converter.handle(response.css('h2.house-info__title').get()).replace('##  ','').strip()
            item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
            item['livingsurface'] = response.xpath("//strong[text()='Totale woonoppervlakte:']/following-sibling::span/text()").get()
            if item['livingsurface']:item['livingsurface']=int(item['livingsurface'].strip().replace(' m',''))
            city =  response.css("div.house-info__city::text").get()
            item['city'] = city.strip()
            item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
            item['rooms'] = response.xpath("//strong[text()='Kamers:']/following-sibling::span/text()").get()
            if item['rooms']: item['rooms']=int(item['rooms'].strip().split()[0])
            item['bedrooms'] = response.xpath("//strong[text()='Slaapkamers:']/following-sibling::span/text()").get()
            if item['bedrooms']: item['bedrooms']=int(item['bedrooms'].strip())
            price=response.css('div.house-info__price::text').get()
            if price:
                item['price']=int(price.strip().replace('.','').replace(',- Per maand','').replace('€','').strip())
            else:
                item['price']=None
            description=''
            for desc in response.css('div.house-overview__description p::text').getall():
                description += desc+'\n'
            item['description'] = description.split('*English*')[0].strip()
            photos=[]
            for photo in response.css('.house-slider__item source[media="(min-width: 1920px)"][type=""]::attr(data-srcset)').getall():
                photos.append('https://www.denederlanden.eu'+photo)
            
            item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
            item['energylabel']=response.xpath("//strong[text()='Energie Label:']/following-sibling::span/text()").get()
            if item['energylabel']:item['energylabel']=item['energylabel'].strip()
            item['countryid']=1
            yield item

        # Decision to proceed to the next page or stop
        if self.items_processed == total_items:
            if self.rented_items_on_page == total_items:
                self.logger.info('All items on this page are rented. Stopping.')
                return
            elif next_page_url:
                yield response.follow('https://www.denederlanden.eu'+next_page_url, self.parse)


if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'denederlanden.json'): {
            'format': 'json',
        }},
        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(DenNederlandenSpider)
    process.start()