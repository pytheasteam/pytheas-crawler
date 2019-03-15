import pymongo
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from typing import List

from crawler.models import ParsedItem


class HTMLDownloaderBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def download(self, url):
        # type: (str) -> BeautifulSoup
        pass


class TargetExtractorBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def extract_targets(self, node, article, current_url):
        # type: (BeautifulSoup, ParsedItem, str) -> List[str]
        pass


class ParserBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, node, url):
        # type: (BeautifulSoup, str) -> ParsedItem
        pass


class ItemStoreBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def store(self, item):
        # type: (ParsedItem) -> None
        pass


class ItemsLoaderBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def load(self):
        # type: () -> pymongo.collection
        pass


class CrawlerBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def crawl(self, url):
        pass
