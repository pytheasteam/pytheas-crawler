from urllib import request
from bs4 import BeautifulSoup
import pymongo
from collections import Counter
from crawler.config import db
# country : city
countries_cities = {
    'united kingdom': 'london',
    'france': 'paris',
    'italy': 'rome',   # + vatican
    'greece': 'crete',
    'indonesia': 'bali',
    'thailand': 'phuket',
    'spain': 'barcelona',
    'turkey': 'istanbul',
    'morocco': 'marrakech',
    'united arab emirates': 'dubai',
    'czech republic': 'prague',
    'cambodia': 'siem reap',
    'new york': 'new york city',
    'jamaica': 'jamaica',
    'vietnam': 'hanoi',
    'japan': 'tokyo',
    'mexico': 'playa del carmen',
    'portugal': 'lisbon',
    'nepal': 'kathmandu',
    'india': 'jaipur',
    'egypt': 'hurghada',
    'china': 'hong kong',
    'peru': 'cusco',
    'australia': 'sydney',
    'israel': 'tel aviv'
}

attraction_counter = Counter()

crawler_db_client = pymongo.MongoClient(
        f'mongodb://{db.USERNAME}:{db.PASSWORD}@{db.HOST}:{db.PORT}/{db.DB}'
    )
pytheas_db = crawler_db_client[db.DB]
all_attractions_collections = pytheas_db[db.ARTICLE_COLLECTION]
count = 0


def get_description_of_attraction(attraction):
    try:
        url = attraction['url']
        html = request.urlopen(url).read()
        bs = BeautifulSoup(html, 'html.parser')
        print("Getting description:")
        desc = '\n'.join([x.text for x in bs.find_all(
            'div', {
                'class': 'attractions-attraction-detail-about-card-AttractionDetailAboutCard__section--1_Efg'
            }
        )])
        print(desc)
        return desc
    except:
        return ""


def get_address_of_attraction(attraction, full=False):
    url = attraction['url']
    try:
        html = request.urlopen(url).read()
        bs = BeautifulSoup(html, 'html.parser')
        location_element = bs.find('span', {'class': 'address'})
    except:
        return None
    try:
        location_span = location_element.find_all('span')[1]
        location_list = location_span.text.lower().split(',')
        try:
            new_location = {
                'street': location_list[0],
                'locality': location_list[1],
                'country': location_list[2]
            }
        except:
            new_location = {
                'street': location_list[0],
                'locality': location_list[1]
            }
        if full:
            return location_span.text.lower()
        print(new_location)
        for country in countries_cities:
            if countries_cities[country].lower() in location_span.text.lower() or country in location_span.text.lower():
                return countries_cities[country]
        print(f"unexpected problem with find city, city: {new_location['locality'].lower()}")
        return None
    except:
        print('unexpected problem with find city!')
        return None


def _update_city_in_crawler_db(attraction_document, new_location):
    all_attractions_collections.update({'_id' : attraction_document['_id']}, {'$set': {'location': new_location}})


def update_attraction(attraction_document):
    print('=======================================================')
    city = get_address_of_attraction(attraction=attraction_document, full=False)
    if city:
        city = city.lower()
        _update_city_in_crawler_db(attraction_document, city)
    else:
        print("Cannot find city")


def update_city(attraction_list):
    global count
    print("start migration: migrate Attractions")
    try:
        while attraction_list:
            print(f"{len(attraction_list)} elements left in list")
            document = attraction_list.pop()
            update_attraction(document)
            count += 1
    except KeyboardInterrupt:
        return
    except:
        print("retry...")
        update_city(attraction_list)


def get_all_attractions_from_db():
    global count
    print(f"Get all attraction from {db.ARTICLE_COLLECTION}")
    all_attractions_cursor = all_attractions_collections.find({}, no_cursor_timeout=True)
    attraction_list = [x for x in all_attractions_cursor]
    print(f"number of attractions: {len(attraction_list)}")
    all_attractions_cursor.close()
    try:
        update_city(attraction_list[count:])
    except:
        print("Error.")


if __name__ == '__main__':
    print("Update cities and location in attractions")
    get_all_attractions_from_db()

