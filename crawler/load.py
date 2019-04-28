import logging
import pymongo
from crawler.abstractions import ItemsLoaderBase

LOGGER = logging.getLogger(__name__)


class MongoItemsLoader(ItemsLoaderBase):

    def __init__(self, host, port, db, items_collection, username=None, password=None):
        self.password = password
        self.username = username
        self.item_collection = items_collection
        self.db = db
        self.port = port
        self.host = host
        LOGGER.info("Connecting to DB... %s:%s", host, port)
        self.client = pymongo.MongoClient(f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}')
        LOGGER.info("Connected to DB.")
        self.db = self.client[db]

    def load(self):
        LOGGER.info("Loading items from db. Collection: %s", self.item_collection)
        return self.db[self.item_collection].find({}, {"url": 1})



