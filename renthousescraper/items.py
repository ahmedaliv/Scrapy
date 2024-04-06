# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class RentalItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field() #is the object rented or available for rent
    url = scrapy.Field() #url to object detail page
    Acceptance = scrapy.Field() #ignore, deprecated
    propertytype = scrapy.Field() #is this an apartment, a house, a studio etc in Dutch: "Object type"
    description = scrapy.Field() #description of the object
    rooms = scrapy.Field() #how many rooms in total in Dutch: "Kamer"
    bedrooms = scrapy.Field() #how many bedrooms in Dutch: "Slaapkamer"
    bathrooms = scrapy.Field() #how many bathrooms in Dutch: "Badkamer"
    street = scrapy.Field() #the street without street number, e.g. "Presenident William Green street " in Dutch: "Straat"
    streetnr = scrapy.Field() #street number with addition, e.g. "12", "12A", "12-3" 
    price = scrapy.Field() #price in euros without decimals, e.g. "2000" for 2000,- euro in Dutch: "Prijs"
    zipcode = scrapy.Field() #zipcode, e.g. "1234AB" in Dutch: "Postcode"
    city = scrapy.Field() #city, e.g. "Amsterdam" in Dutch: "Stad/Plaats"
    province = scrapy.Field() #province (if available), e.g. "Noord-Holland"
    lat = scrapy.Field() #latitude (if available, e.g. from Google Maps element, data layer, metadata), e.g. "51.54554621222"
    lon = scrapy.Field() #longitude, same as latitude
    photos = scrapy.Field() #links to the full size photos, e.g. "https://www.example.com/media/12124545.jpg"
    thumbnails = scrapy.Field() #ignore, deprecated
    construction_type = scrapy.Field() # type of construction (if available), e.g. "nieuwbouw" or "bestaande bouw"
    construction_year = scrapy.Field() #year of construction (if available), e.g. "1975" in Dutch: "Bouwjaar"
    deposit = scrapy.Field() #how much deposit to be paid (if available), e.g. "3000"
    livingsurface = scrapy.Field() #square meters of the home, integer value, e.g, "123" in Dutch: "(Woon)Oppervlakte"
    totalvolume = scrapy.Field() #volume of home, integer value, e.g. "454" in Dutch: "Inhoud"
    floor = scrapy.Field() #what floor is the apartment on (if available), integer value, e.g "3" in Dutch: "Verdieping"
    totalfloors = scrapy.Field() #how many floors does the home have (if available), integer value, e.g. "2"
    features = scrapy.Field()  #ignore, deprecated
    parking = scrapy.Field() # does the house include parking (if available), boolean value, 1 or 0
    furnishedstate = scrapy.Field() #is the home upholstered, furnished (if available), string value e.g. "gemeubileerd"
    energylabel = scrapy.Field() #energy label (if available), e.g. "A" or "A+", "G"
    servicecosts = scrapy.Field() #montly service costs (if available), integer value, e.g. "500"
    availablefromdate = scrapy.Field() #from when is this home available (if available), date, e.g. "01-01-2025"
    countryid = scrapy.Field() # set to always integer value "1"

    pass
