import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import html2text
import re
import json
from scrapy.crawler import CrawlerProcess
from renthousescraper.items import RentalItem
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.http import HtmlResponse
import os
converter = html2text.HTML2Text()
converter.ignore_links = True
converter.ignore_images = True 

class grandrelocationSpider(scrapy.Spider):
    name = 'grandrelocation'
    
    def start_requests(self):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ar,ar-EG;q=0.9,en-GB;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5,en-US;q=0.4',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.grandrelocation.nl',
            'Pragma': 'no-cache',
            'Referer': 'https://www.grandrelocation.nl/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        body = 'action=all_houses&api=25abab1e7685b3d249a473b6d8d371b5&offsetRow=0&numberRows=100&leased_wr_last=false&leased_last=false&sold_wr_last=false&sold_last=false&path=%2Fwoning-aanbod%3Finterior%3D14&html_lang=nl'
        
        yield scrapy.Request(
            url='https://cdn.eazlee.com/eazlee/api/query_functions.php',
            method='POST',
            headers=headers,
            body=body,
            callback=self.parse
        )
        
    def parse(self, response):
        # create new RentalItem which will saved to json file
        res=json.loads(response.text)
        ''
        for it in res:
            if it['front_status'] == 'Beschikbaar':
                item = RentalItem()
                item_id= it['house_id']
                city =  it['city']
                street=it['street']
                street=street.replace(' ','-')
                url=f'https://www.grandrelocation.nl/woning?{city}/{street}/{item_id}'
                item['url'] = url
                item['id']=it['house_id']
                item['propertytype']=it['property_type_1']
                item['livingsurface']=it['surface']
                if item['livingsurface']:item['livingsurface']=int(item['livingsurface'])
                item['rooms']=it['rooms']
                item['price']=it['price']
                if item['price']:item['price']=int(item['price'])
                item['servicecosts']=it['forsale_service_costs']
                if item['servicecosts']:item['servicecosts']=float(item['servicecosts'])
                item['streetnr']=it['number']
                item['street']=it['street']
                item['zipcode']=it['zipcode']
                item['city']=it['city']
                item['rooms']=int(it['rooms'])
                item['bedrooms']=int(it['bedrooms'])
                item['bathrooms']=int(it['bathrooms'])
                if item['rooms']==0:item['rooms']=None
                if item['bathrooms']==0:item['bathrooms']=None
                if item['bedrooms']==0:item['bedrooms']=None
                photos=it['photos_all']
                mod_photos=[]
                for photo in photos:
                    photo=photo.replace('\/','/')
                    mod_photos.append(photo)
                item['photos'] = ';'.join(mod_photos)
                item['countryid']=1
                yield item


    #     yield item
if __name__ == "__main__":
    Settings = {
        'DOWNLOADER_MIDDLEWARES' : {
            'scrapy_selenium.SeleniumMiddleware': 800
        },
        # Specify the output location and format
        'FEEDS': {os.path.join('result folder', 'grandrelocation.json'): {
            'format': 'json',
        }},

        # Define user agent to simulate a web browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Create a Scrapy CrawlerProcess with specified settings
    process = CrawlerProcess(Settings)

    # Start crawling using the defined spider
    process.crawl(grandrelocationSpider)
    process.start()