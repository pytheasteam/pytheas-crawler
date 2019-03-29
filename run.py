import logging
import pymongo
from crawler.config import db
from crawler.config.crawler import TRIPADVISOR_BASE_URL, TRIPADVISOR_PARSER_MAPPING
from crawler.crawler import Crawler
from crawler.downloader import HTMLDownloader
from crawler.parse.tripadvisor import TripAdvisorParser, AttractionParser, RestaurantParser
from crawler.store import MongoItemStore


def main():
    _setup_logging()
    downloader = HTMLDownloader()

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

    parser_mapping = {}
    urls_to_crawl = []
    parser_mapping.update(TRIPADVISOR_PARSER_MAPPING)
    urls_to_crawl.append(TRIPADVISOR_BASE_URL)

    crawler = Crawler(downloader, parser_mapping, store, collection)
    crawler.crawl(urls_to_crawl)


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
