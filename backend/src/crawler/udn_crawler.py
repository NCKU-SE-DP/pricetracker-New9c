"""
UDN News Scraper Module

This module provides the UDNCrawler class for fetching, parsing, and saving news articles from the UDN website.
The class extends the NewsCrawlerBase and includes functionalities to search for news articles based on a search term,
parse the details of individual articles, and save them to a database using SQLAlchemy ORM.

Classes:
    UDNCrawler: A class to scrape news from UDN.

Exceptions:
    DomainMismatchException: Raised when the URL domain does not match the expected domain for the crawler.

Usage Example:
    crawler = UDNCrawler(timeout=10)
    headlines = crawler.startup("technology")
    for headline in headlines:
        news = crawler.parse(headline.url)
        crawler.save(news, db_session)

UDNCrawler Methods:
    __init__(self, timeout: int = 5): Initializes the crawler with a default timeout for HTTP requests.
    startup(self, search_term: str) -> list[Headline]: Fetches news headlines for a given search term across multiple pages.
    get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]: Fetches news headlines for specified pages.
    _fetch_news(self, page: int, search_term: str) -> list[Headline]: Helper method to fetch news headlines for a specific page.
    _create_search_params(self, page: int, search_term: str): Creates the parameters for the search request.
    _perform_request(self, params: dict): Performs the HTTP request to fetch news data.
    _parse_headlines(response): Parses the response to extract headlines.
    parse(self, url: str) -> News: Parses a news article from a given URL.
    _extract_news(soup, url: str) -> News: Extracts news details from the BeautifulSoup object.
    save(self, news: News, db: Session): Saves a news article to the database.
    _commit_changes(db: Session): Commits the changes to the database with error handling.
"""

import requests
from bs4 import BeautifulSoup
from pydantic import TypeAdapter
from sqlalchemy.orm import Session
from urllib.parse import quote
from .crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary
from ..models import NewsArticle

class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2
    NEWS_WEBSITE_URL = "https://udn.com/api/more"

    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout

    def startup(self, search_term: str) -> list[Headline]:
        return self.get_headline(search_term, page=(1, 10))

    def get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]:
        page_range = range(page[0], page[1] + 1) if isinstance(page, tuple) else [page]
        headlines = []
        for p in page_range:
            headlines.extend(self._fetch_news(p, search_term))
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        params = self._create_search_params(page, search_term)
        response = self._perform_request(url=UDNCrawler.NEWS_WEBSITE_URL, params=params)
        return UDNCrawler._parse_headlines(response)

    def _create_search_params(self, page: int, search_term: str) -> dict:
        parameters = {
            "page": page,
            "id": f"search:{quote(search_term)}",
            "channelId": UDNCrawler.CHANNEL_ID,
            "type": "searchword",
        }
        return parameters

    def _perform_request(self, url: str | None = None, params: dict | None = None) -> requests.Response:
        response = requests.get(url=url, params=params)
        return response

    @staticmethod
    def _parse_headlines(response: requests.Response) -> list[Headline]:
        return TypeAdapter(list[Headline]).validate_python(response.json()["lists"])

    def parse(self, url: str) -> News:
        response = self._perform_request(url=url)
        soup = BeautifulSoup(response.text, "html.parser")
        return self._extract_news(soup, url)

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News:
        """
        Extracts news details from the BeautifulSoup object.
    
        :param soup: The BeautifulSoup object containing the parsed HTML.
        :param url: The URL of the news article.
        :return: A News object with the extracted title, time, and content.
        """
        try:
            # Extract the title
            title = soup.find("h1", class_="article-content__title").text.strip()
    
            # Extract the publication time
            time = soup.find("time", class_="article-content__time").text.strip()
    
            # Extract the article content
            content_section = soup.find("section", class_="article-content__editor")
            paragraphs = [
                paragraph.text.strip()
                for paragraph in content_section.find_all("p")
                if paragraph.text.strip() and "▪" not in paragraph.text
            ]
            content = " ".join(paragraphs)
    
            return News(title=title, url=url, time=time, content=content)
        except Exception as e:
            print(f"Error extracting news: {e}")
            pass

    def save(self, news: NewsWithSummary, db: Session):
        """
        Saves a news article to the database.
    
        :param news: The News object to save.
        :param db: The SQLAlchemy database session.
        """
        try:
            if db:
                db.add(NewsArticle(**news.model_dump()))
                db.commit()
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error saving news: {e}")

    @staticmethod
    def _commit_changes(db: Session):
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Database commit failed: {e}")
