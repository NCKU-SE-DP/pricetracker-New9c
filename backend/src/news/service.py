import itertools
import json
from openai import OpenAI
import requests
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session
from urllib.parse import quote
from . import utils
from .config import configuration
from ..models import NewsArticle, User, user_news_association_table
from ..crawler.crawler_base import NewsWithSummary
from ..crawler.udn_crawler import UDNCrawler
from ..llm_client.openai_client import OpenAIClient
from ..llm_client.anthropic_client import AnthropicClient
from ..llm_client.base import RelevanceEvaluation


_id_counter = itertools.count(start=1000000)
crawler = UDNCrawler()
openai_client = OpenAIClient(api_key=configuration.open_ai_api_key)
anthropic_client = AnthropicClient(api_key=configuration.anthropic_api_key)

def _generate_news_id() -> int:
    return next(_id_counter)

def _news_exists(news_id, db: Session): # id2 does not say what it does
    return db.query(NewsArticle).filter_by(id=news_id).first() is not None



def summarize_news(content: str, model:str = "open_ai") -> dict[str, str]|None:
    summary = None
    if model == "open_ai":
        summary = openai_client.generate_summary(content)
    elif model == "anthropic":
        summary = anthropic_client.generate_summary(content)
    return summary


def _search(search_term, is_initial=False):
    if is_initial:
        return crawler.startup(search_term)
    return crawler.get_headline(search_term, page=1)

def get_new(db:Session, is_initial=False):
    """
    get new info

    :param is_initial:
    :return:
    """
    news_data = _search("價格", is_initial=is_initial)
    for news in news_data:
        relevance = openai_client.evaluate_relevance(news["title"])
        if relevance == RelevanceEvaluation.HIGH:
            news = crawler.validate_and_parse(news.url)
            if news is None:
                continue
            summary = summarize_news(news.content)
            news_with_summary = NewsWithSummary(
                title=news.title,
                url=news.url,
                time=news.time,
                content=news.content,
                summary=summary["影響"],
                reason=summary["原因"]
            )
            crawler.save(news_with_summary, db)

def _get_article_upvote_details(article_id, user_id, db): #make it more understandable
    counted_upvotes = ( # I assume this is how many upvotes the article has
        db.query(user_news_association_table)
        .filter_by(news_articles_id=article_id)
        .count()
    )
    voted = False
    if user_id:
        voted = (
                db.query(user_news_association_table)
                .filter_by(news_articles_id=article_id, user_id=user_id)
                .first()
                is not None
        )
    return counted_upvotes, voted

def toggle_upvote(news_id, user_id, db): # make it clear
    existing_upvote = db.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == news_id,
            user_news_association_table.c.user_id == user_id,
        )
    ).scalar()

    if existing_upvote:
        delete_upvote = delete(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == news_id,
            user_news_association_table.c.user_id == user_id,
        ) # I don't know what stmt is, I just think this tells what it does better.
        db.execute(delete_upvote)
        db.commit()
        return "Upvote removed"
    else:
        insert_upvote= insert(user_news_association_table).values(
            news_articles_id=news_id, user_id=user_id
        )
        db.execute(insert_upvote)
        db.commit()
        return "Article upvoted"


def retrieve_news_with_upvote_status(database: Session, user: User | None):
    news_list = database.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    news_list_adding_upvote_status = []
    for news in news_list:
        upvotes, is_upvoted = _get_article_upvote_details(news.id, (None if user is None else user.id), database)
        news_list_adding_upvote_status.append(
            {**news.__dict__, "upvotes": upvotes, "is_upvoted": is_upvoted}
        )
    return news_list_adding_upvote_status

def search_news(prompt: str) -> list:
    news_list = []
    keywords = openai_client.extract_search_keywords(prompt)
    # should change into simple factory pattern
    news_snapshots = _search(keywords, is_initial=False)
    for snapshot in news_snapshots:
        try:
            news = crawler.validate_and_parse(snapshot.url).model_dump()
            news["id"] = _generate_news_id()
            news_list.append(news)
        except Exception as exception:
            print(exception)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)
