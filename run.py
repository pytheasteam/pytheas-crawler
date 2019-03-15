import logging
import pymongo
from crawler.config import db
from crawler.crawler import Crawler
from crawler.downloader import SeleniumHTMLDownloader, HTMLDownloader
from crawler.parse.tripadvisor import TripAdvisorParser, AttractionParser, RestaurantParser
from crawler.store import MongoItemStore
from crawler.load import MongoItemsLoader


def main():
    _setup_logging()
    # downloader = SeleniumHTMLDownloader('./chromedriver')
    downloader = HTMLDownloader()
    # mongodb://<dbuser>:<dbpassword>@ds215633.mlab.com:15633/pytheas

    db_client = pymongo.MongoClient(f'mongodb://{db.USERNAME}:{db.PASSWORD}@{db.HOST}:{db.PORT}/{db.DB}')
    collection = db_client[db.DB][db.ARTICLE_COLLECTION]

    store = MongoItemStore(
        host='ds215633.mlab.com',
        port='15633',
        db='pytheas',
        article_collection='restaurants',
        username='pytheas',
        password='pytheas1'
    )

    items_loader = MongoItemsLoader(
        host='ds215633.mlab.com',
        port='15633',
        db='pytheas',
        items_collection='paris_test_new',
        username='pytheas',
        password='pytheas1'
    )

    # test_collection = db_client.pytheas['test']
    # query = {"location": {"$regex": ".*Paris.*"}}
    # paris = test_collection.find(query)
    # names = set()
    # attractions = []
    # for attraction in paris:
    #     if attraction['name'] not in names:
    #         names.add(attraction['name'])
    #         attractions.append(attraction)
    # paris_urls = []
    # for attraction in attractions:
    #     paris_urls.append(attraction['url'])

    crawler = Crawler(downloader, {
        'www.tripadvisor.com/TravelersChoice-Destinations': TripAdvisorParser(),
        # 'www.tripadvisor.com/Attraction_Review': AttractionParser(),
        'www.tripadvisor.com/Attractions': AttractionParser(),
        'www.tripadvisor.com/Restaurant_Review': RestaurantParser(),
        'www.tripadvisor.com/Restaurants': RestaurantParser()
    }, store, collection)
    crawler.crawl('https://www.tripadvisor.com/TravelersChoice-Destinations')


def _setup_logging():
    # create logger
    logger = logging.getLogger('crawler')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


if __name__ == '__main__':
    main()
