from urllib import request
from bs4 import BeautifulSoup
from selenium import webdriver

from crawler.abstractions import HTMLDownloaderBase


class SeleniumHTMLDownloader(HTMLDownloaderBase):

    def __init__(self, webdriver_path):
        self.webdriver_path = webdriver_path
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--dns-prefetch-disable')
        self.options.add_argument('headless')

    def download(self, url):
        driver = webdriver.Chrome(self.webdriver_path, chrome_options=self.options)
        driver.get(url)
        html = driver.page_source
        return BeautifulSoup(html, 'html.parser')


class HTMLDownloader(HTMLDownloaderBase):
    def download(self, url):
        html = request.urlopen(url).read()
        return BeautifulSoup(html, 'html.parser')


class CommentDownloader(HTMLDownloaderBase):

    def download(self, url):
        pass

    def download_with_params(self, url, params):
        pass
