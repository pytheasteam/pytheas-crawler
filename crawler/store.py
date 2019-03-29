import logging
import pymongo
from crawler.abstractions import ItemStoreBase

LOGGER = logging.getLogger(__name__)

MAX_RETRY = 3


class MongoItemStore(ItemStoreBase):
    def __init__(self, host, port, db, article_collection, username=None, password=None):
        self.password = password
        self.username = username
        self.article_collection = article_collection
        self.db = db
        self.port = port
        self.host = host
        LOGGER.info("Connecting to DB... %s:%s", host, port)
        self.client = pymongo.MongoClient(f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}')
        LOGGER.info("Connected to DB.")
        self.db = self.client[db]
        self.retry = 0

    def store(self, item):
        LOGGER.info("Storing article to db. URL: %s", item.url)
        try:
            self.db[self.article_collection].insert_one(vars(item))
            self.retry = 0
        except:
            if self.retry < MAX_RETRY:
                self.client = pymongo.MongoClient(
                    f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}'
                )
                LOGGER.info("Connected to DB.")
                self.db = self.client[self.db]
                self.retry += 1
                self.store(item)
            else:
                raise Exception
