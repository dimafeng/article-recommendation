import logging
from newspaper import Article
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from abc import ABC, abstractmethod
from typing import final

from article_recs.content_extraction.paywall import getUnpaywalledUrls, ispaywall

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NotArticleException(Exception):
    "Raised when content is not an article"
    pass

class Scraper(ABC):
    def __init__(self):
        self.__article: Article = None 

    @final
    def load(self, url) -> None:
        self._load(url)
        self.__article = Article('')

    @abstractmethod
    def _load(self, url):
        pass

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_html_content(self):
        pass

    def __get_article_instance(self):
        if not self.__article.is_parsed:
            self.__article.set_html(self.get_html_content())
            self.__article.parse()

        return self.__article

    def get_meta_data(self) -> dict:
        article = self.__get_article_instance()
        return {
            "title": article.title,
            "authors": article.authors,
            "publish_date": article.publish_date.isoformat() if article.publish_date else None,
            "top_image": article.top_image,
            "movies": article.movies
        }
    
    def get_plain_text(self) -> str:
        return self.__get_article_instance().text

    def get_article_html(self) ->  str:

        return self.__get_article_instance().config.get_parser().nodeToString(self.__get_article_instance().top_node)
    
    def is_article(self) -> bool:
        return self.__count_words(self.get_plain_text()) > 100
    
    def get_page_links(self):
        soup = BeautifulSoup(self.get_html_content(), 'html.parser')
        links = soup.find_all('a')
        return [link.get('href') for link in links]

    def __count_words(self, text):
        return len(text.split(" "))

class SimpleScraper(Scraper):
    def __init__(self):
        super().__init__()

    def _load(self, url: str):
        self.url = url
        self.__html_content = self.__scrape_html_content(url, 2)

    def get_title(self):
        return self.__html_content.find(".//title").text

    def __scrape_html_content(self, url, retries=3):
        for i in range(retries):
            try:
                logging.info(f"Simple scraper: {url}")
                html_content = requests.get(url, verify=False, timeout=20).content
                
                return html_content
            except requests.exceptions.RequestException as e:
                logging.warning(f"Simple scraper: Request failed for {url} due to {e}. Retrying in 5 seconds...")
                time.sleep(5)
                continue

        # if all retries fail, raise an exception
        raise NotArticleException("Content is not an article")

    def get_html_content(self):
        return self.__html_content

class SeleniumScraper(Scraper):
    def __init__(self, selenium_url: str):
        super().__init__()
        self.__selenium_url = selenium_url

    def _load(self, url):
        self.url = url
        self.__html_content = self.__scrape_html_content(url, 2)

    def get_title(self):
        return self.__html_content.title

    def __is_page_loaded(self, driver):
        #find all h1,h2,h3,h4,h5,h6 tags
        headings = driver.find_elements(by=By.XPATH, value="//h1|//h2|//h3|//h4|//h5|//h6")

        return driver.execute_script("return document.readyState") == "complete" and len(headings) > 0

    def __scrape_html_content(self, url, retries=3):
        for i in range(retries):
            try:
                logging.info(f"Selenium scraper: {url}")
                chrome_options = webdriver.ChromeOptions()
                driver = webdriver.Remote(
                    command_executor=self.__selenium_url,
                    options=chrome_options
                )
                #driver = webdriver.Chrome()
                driver.get(url)

                for t in range(10):
                    # wait for the page to load
                    time.sleep(1)
                    if self.__is_page_loaded(driver):
                        break

                # get the HTML content from the webpage
                html_content = driver.page_source

                # close the webdriver
                driver.quit()

                return html_content
            except WebDriverException:
                # if there's an error, retry after waiting for 5 seconds
                time.sleep(2)
                continue

        # if all retries fail, raise an exception
        raise Exception(f"Failed to scrape {url} after {retries} retries")

    def get_html_content(self):
        return self.__html_content

class PaywallScraperStrategy(Scraper):
    def __init__(self, basic_scraper: Scraper, advanced_scraper: Scraper):
        super().__init__()
        self.__basic_scraper = basic_scraper
        self.__advanced_scraper = advanced_scraper
        self.__scraper = basic_scraper

    def _load(self, url):
        
        # if the url is not a paywall, use the basic scraper
        if not ispaywall(url):
            self.__scraper = self.__basic_scraper
            self.__scraper.load(url)

            if self.__basic_scraper.is_article():
                return
            
            self.__scraper = self.__advanced_scraper
            self.__scraper.load(url)
            
            return

        self.__scraper = self.__advanced_scraper

        # if the url is a paywall, try to unpaywall it
        for url in getUnpaywalledUrls(url):
            logging.info(f"Trying to unpaywall with {url}")
            try:
                if 'archive.is' in url:
                    self.__scraper.load(url)
                    logging.info(self.__scraper.get_page_links())
                    for link in self.__scraper.get_page_links():
                        if 'https://archive.is/' in link and len(link) < 25:
                            url = link

                self.__scraper.load(url)
                if self.__scraper.is_article():
                    return
            except Exception as e:
                #logging.critical(e, exc_info=True)
                logging.error(f"Failed to unpaywall {url}: {e}")
                continue
        
        raise Exception(f"Failed to load {url}")

    def get_title(self):
        return self.__scraper.get_title()

    def get_html_content(self):
        return self.__scraper.get_html_content()