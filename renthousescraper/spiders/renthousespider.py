import re
from renthousescraper.items import RenthousescraperItem
import scrapy


class RenthousespiderSpider(scrapy.Spider):
    name = "renthousespider"
    allowed_domains = ["renthousevastgoed.nl"]
    start_urls = ["https://renthousevastgoed.nl/aanbod/?_paged=1"]

    def parse(self, response):        
                # Extract URLs of property items
        property_listings = response.css('.col-12.col-lg-6.col-xl-4')


        rented_found = False
        for property_listing in property_listings:
            # Check if the property is rented
            if "Verhuurd" in property_listing.extract():
                rented_found = True
                print('*************************')
                print('Rented Link: ',property_listing.css('.object-image a::attr(href)').get())
                self.logger.info("Rented property found, stopping parsing...")
                return

            # Extract property link
            link = property_listing.css('.object-image a::attr(href)').get()
            yield response.follow(link, self.parse_property)
            
        if not rented_found:
            current_page = int(re.search(r'_paged=(\d+)', response.url).group(1))
            next_page = f"https://renthousevastgoed.nl/aanbod/?_paged={current_page + 1}"
            if not response.css('.col-12.col-lg-6.col-xl-4'):
                self.logger.info("No more pages to scrape, stopping parsing...")
                return  
            yield response.follow(next_page, self.parse)

    def parse_property(self, response):
        # Extract data from the property page
        item = RenthousescraperItem()
            # Extracting address details
        address_lines = response.css('.object-address-line')

        # Extracting street, house number, zipcode, and place
        street = address_lines[0].css('.object-street::text').get()
        house_number = address_lines[0].css('.object-housenumber::text').get()
        zipcode = address_lines[1].css('.object-zipcode::text').get()
        place = address_lines[1].css('.object-place::text').get()
        
        # Assigning address details to item
        item['street'] = street
        item['house_number'] = house_number
        item['zipcode'] = zipcode
        item['place'] = place

        # Extracting details
        item['price'] = response.css('.object-price-rent .object-price-value::text').get(default='N/A').strip()
        item['rental_agreement'] = response.css('.object-feature-beschikbaarheid .object-feature-info::text').get(default='N/A').strip()
        item['offered_since'] = response.css('.object-feature-date-release .object-feature-info::text').get(default='N/A').strip()
        item['status'] = response.css('.object-feature-status .object-feature-info::text').get(default='N/A').strip()
        item['acceptance'] = response.css('.object-feature-aanvaarding .object-feature-info::text').get(default='N/A').strip()
        item['type_of_house'] = response.css('.object-feature-woonhuissoort .object-feature-info::text').get(default='N/A').strip()
        item['type_of_construction'] = response.css('.object-feature-bouwvorm .object-feature-info::text').get(default='N/A').strip()
        item['specifically'] = response.css('.object-feature-bijzonderheden .object-feature-info::text').get(default='N/A').strip()
        item['location'] = response.css('.object-feature-liggingen .object-feature-info::text').get(default='N/A').strip()
        item['living_area'] = response.css('.object-feature-woonoppervlakte .object-feature-info::text').get(default='N/A').strip()
        item['contents'] = response.css('.object-feature-inhoud .object-feature-info::text').get(default='N/A').strip()
        item['number_of_rooms'] = response.css('.object-feature-aantalkamers .object-feature-info::text').get(default='N/A').strip()
        item['number_of_bathrooms'] = response.css('.object-feature-aantalbadkamers .object-feature-info::text').get(default='N/A').strip()
        item['bathroom_amenities'] = response.css('.object-feature-badkamersvoorzieningen .object-feature-info::text').get(default='N/A').strip()
        item['number_of_floors'] = response.css('.object-feature-aantaletages .object-feature-info::text').get(default='N/A').strip()
        item['energy_label'] = response.css('.object-features-energy .object-feature-info::text').get(default='N/A').strip()
        item['insulation'] = response.css('.object-feature-isolatievormen .object-feature-info::text').get(default='N/A').strip()
        item['heating'] = response.css('.object-feature-verwarmingsoorten .object-feature-info::text').get(default='N/A').strip()
        item['hot_water'] = response.css('.object-feature-warmwatersoorten .object-feature-info::text').get(default='N/A').strip()
        item['garden'] = response.css('.object-feature-tuintypes .object-feature-info::text').get(default='N/A').strip()
        item['backyard_area'] = response.css('.object-feature-hoofdtuinoppervlakte .object-feature-info::text').get(default='N/A').strip()
        item['garden_location'] = response.css('.object-feature-hoofdtuinlocatie .object-feature-info::text').get(default='N/A').strip()
        item['storage_space'] = response.css('.object-feature-schuurbergingsoort .object-feature-info::text').get(default='N/A').strip()
        item['parking'] = response.css('.object-feature-parkeerfaciliteiten .object-feature-info::text').get(default='N/A').strip()

        # Extracting images
        image_elements = response.css('div.object-detail-photos-v3 img')
        image_urls = [img.attrib['data-src'] for img in image_elements]
        item['images'] = image_urls
        yield item