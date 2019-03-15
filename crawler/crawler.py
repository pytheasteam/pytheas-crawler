import logging
import re
from typing import Optional
from crawler.abstractions import CrawlerBase
from crawler.parse.abstractions import WebsiteParserBase

LOGGER = logging.getLogger(__name__)


class Crawler(CrawlerBase):

    def __init__(self, downloader, parser_mapping, article_store, db):
        self.article_store = article_store
        self.parser_mapping = parser_mapping
        self.downloader = downloader
        self.db = db
        self.exist_urls = []

    def _load_exist_urls(self):
        collection = self.db.load()
        return [doc['url'] for doc in collection]

    def _is_in_db(self, url):
        self.db.find_one({"url": url})

    def crawl(self, url):
        if type(url) is list:
            urls_to_crawl = url
        else:
            urls_to_crawl = [url]
        while len(urls_to_crawl) > 0:
            collected_targets = []
            for url in urls_to_crawl:
                in_db = self.db.find({"url": url}).count()
                # for Debug
                LOGGER.info("Searching for a matching parser. URL: %s", url)
                parser = self._get_matching_parser(url)
                if parser is not None:
                    LOGGER.info("Downloading web page. URL: %s", url)
                    page_node = self.downloader.download(url)
                    article = None
                    if not in_db:
                        LOGGER.info("Parsing web page to Article. URL: %s", url)
                        article = parser.parse(page_node, url)
                        if article and not in_db:
                            self.article_store.store(article)
                        elif not article:
                            LOGGER.info("No article could be parsed from web page. URL: %s", url)
                    else:
                        LOGGER.info("URL already exist in db! URL: %s", url)
                    next_targets = parser.extract_targets(node=page_node, article=article, current_url=url)
                    next_targets = [target.split('#')[0] for target in next_targets]
                    next_targets = list(set(next_targets))
                    collected_targets.extend(next_targets)
                    collected_targets = list(set(collected_targets))
                else:
                    LOGGER.info("No parser was found for the url. skipping. URL: %s", url)
            urls_to_crawl = collected_targets

    def _get_matching_parser(self, link):
        # type: (str) -> Optional[WebsiteParserBase]
        for pattern, parser in self.parser_mapping.items():
            try:
                if re.search(pattern, link) is not None:
                    return parser
            except re.error as ex:
                LOGGER.warning(f'Parser regex is not valid!. parser_type: %s, reason: {ex}', parser.__class__.__name__)
        return None
