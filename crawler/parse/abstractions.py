from abc import ABCMeta
from crawler.abstractions import TargetExtractorBase, ParserBase


class WebsiteParserBase(TargetExtractorBase, ParserBase):
    __metaclass__ = ABCMeta
    pass
