# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RenthousescraperItem(scrapy.Item):
    
    price = scrapy.Field()
    rental_agreement = scrapy.Field()
    offered_since = scrapy.Field()
    status = scrapy.Field()
    acceptance = scrapy.Field()
    type_of_house = scrapy.Field()
    type_of_construction = scrapy.Field()
    specifically = scrapy.Field()
    location = scrapy.Field()
    living_area = scrapy.Field()
    contents = scrapy.Field()
    number_of_rooms = scrapy.Field()
    number_of_bathrooms = scrapy.Field()
    bathroom_amenities = scrapy.Field()
    number_of_floors = scrapy.Field()
    energy_label = scrapy.Field()
    insulation = scrapy.Field()
    heating = scrapy.Field()
    hot_water = scrapy.Field()
    garden = scrapy.Field()
    backyard_area = scrapy.Field()
    garden_location = scrapy.Field()
    storage_space = scrapy.Field()
    parking = scrapy.Field()
    # Address fields
    street = scrapy.Field()
    house_number = scrapy.Field()
    zipcode = scrapy.Field()
    place = scrapy.Field()
    images = scrapy.Field()