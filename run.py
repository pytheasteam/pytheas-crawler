import logging
import pymongo
from crawler.config import db
from crawler.config.crawler import TRIPADVISOR_BASE_URL, TRIPADVISOR_PARSER_MAPPING, TRIPADVISOR_RESTAURANTS_BASE_URL
from crawler.crawler import Crawler
from crawler.downloader import HTMLDownloader
from crawler.store import MongoItemStore


def main():
    _setup_logging()
    downloader = HTMLDownloader()

    db_client = pymongo.MongoClient(f'mongodb://{db.USERNAME}:{db.PASSWORD}@{db.HOST}:{db.PORT}/{db.DB}')
    collection = db_client[db.DB][db.ARTICLE_COLLECTION]

    store = MongoItemStore(
        host=db.HOST,
        port=db.PORT,
        db=db.DB,
        article_collection=db.ARTICLE_COLLECTION,
        username=db.USERNAME,
        password=db.PASSWORD
    )

    parser_mapping = {}
    urls_to_crawl = []
    parser_mapping.update(TRIPADVISOR_PARSER_MAPPING)
    urls_to_crawl.append(TRIPADVISOR_RESTAURANTS_BASE_URL)

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
