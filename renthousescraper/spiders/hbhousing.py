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
class hbhousingSpider(scrapy.Spider):
    name = 'hbhousing'
    start_urls = ['https://www.hbhousing.nl/aanbod/huur/']
    def parse(self, response):
            links=response.css('article.woning.AVAILABLE a::attr(href)').getall()
            for i in range(len(links)):
                listing_url =  links[i]
                yield scrapy.Request(
                    url=listing_url, 
                    callback=self.parse_object,
                )
            next_page_url = response.css('a.next.page-numbers::attr(href)').get()
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
        item['status'] = 'available' # we only visit the available items
        item['title']=response.xpath("(//header[(@class='text-left')]/h1)[1]/text()").get().strip()
        # item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['livingsurface'] = response.xpath("//td[contains(text(),'Woonoppervlakte')]/following-sibling::td/text()").get().replace('m','')
        if item['livingsurface']:item['livingsurface']=int(item['livingsurface'])
        item['totalvolume']=response.xpath("//td[contains(text(),'Inhoud')]/following-sibling::td/text()").get().replace('m','')
        if item['totalvolume']:item['totalvolume']=int(item['totalvolume'])
        item['propertytype'] = response.xpath("//td[contains(text(),'Soort object')]/following-sibling::td/text()").get()
        if item['propertytype']:item['propertytype']=item['propertytype'].strip()
        address=response.xpath("(//div[@class='address-holder'])[1]/text()").get().strip()
        city =  address.split()[-1]
        item['city'] = city
        item['street'], item['streetnr'] = getStreet_StreetNr(item['title'])
        item['zipcode']=address.split()[0]+address.split()[1].replace(',','')
        item['rooms'] = response.xpath("//td[contains(text(),'Kamers')]/following-sibling::td/text()").get()
        if item['rooms']: item['rooms']=int(item['rooms'])
        item['bathrooms'] = response.xpath("//td[contains(text(),'Slaapkamers')]/following-sibling::td/text()").get()
        if item['bathrooms']: item['bathrooms']=int(item['bathrooms'])
        price=response.xpath("//td[contains(text(),'Huurprijs')]/following-sibling::td/text()").get()
        if price:
            item['price']=price.replace('€','').replace(',-','').replace('.','').strip()
        else:
            item['price']=None
        description=''
        for desc in response.css('div.the-content-holder p::text').getall():
            description += desc+'\n'
        item['description'] = description.strip()
        photos=[]
        for photo in response.css('div.property-images-holder.more-images div.image-holder::attr(style)').getall():
            pattern = r'url\((.*?)\)'
            match = re.search(pattern, photo)
            url=match.group(1)
            photos.append(url)
        parking=0
        attributes=response.css('div.property-attribute div.attribute-label::text').getall()
        if 'Parkeren' in attributes:parking=1
        item['parking']=parking
        if 'gemeubileerd' in description:
            item['furnishedstate']='furnished'
        item['photos'] = ';'.join(photos)#ensure semicolon is used as separator between image URLs
        item['countryid']=1
        item['lat'] = response.xpath('//meta[@itemprop="latitude"]/@content').get()
        if item['lat']:item['lat']=float(item['lat'])
        item['lon'] = response.xpath('//meta[@itemprop="longitude"]/@content').get()
        if item['lon']:item['lon']=float(item['lon'])
        yield item

if __name__ == "__main__":
    Settings = {
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'hbhousing.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(hbhousingSpider)
    process.start()