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


_id_counter = itertools.count(start=1000000)

def _generate_news_id() -> int:
    return next(_id_counter)

def _news_exists(news_id, db: Session): # id2 does not say what it does
    return db.query(NewsArticle).filter_by(id=news_id).first() is not None

def _ask_openAI(system_prompt: str, user_prompt: str) -> str | None:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    completion = OpenAI(api_key=configuration.open_ai_api_key).chat.completions.create(
        model=configuration.open_ai_model,
        messages=messages
    )
    response = completion.choices[0].message.content
    return response


def _extract_search_keywords(news_expectation: str) -> str | None:
    keywords = _ask_openAI(
        system_prompt="你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
        user_prompt=news_expectation
    )
    return keywords
def summarize_news(content: str) -> dict:
    summary = _ask_openAI(
        system_prompt="你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
        user_prompt=content
    )
    return json.loads(summary)


def _add_new(news_data, db: Session):
    """
    add new to db
    :param news_data: news info
    :return:
    """
    db.add(NewsArticle(
        url=news_data["url"],
        title=news_data["title"],
        time=news_data["time"],
        content=news_data["content"],
        summary=news_data["summary"],
        reason=news_data["reason"],
    ))
    db.commit()

def _get_new_info(search_term, is_initial=False):
    """
    get new

    :param search_term:
    :param is_initial:
    :return:
    """
    all_news_data = []
    # iterate pages to get more news data, not actually get all news data
    if is_initial: # clear up meaning
        all_lists= []
        for page_num in range(1, 10):
            parameters = {
                "page": page_num,
                "id": f"search:{quote(search_term)}",
                "channelId": 2,
                "type": "searchword",
            }
            response = requests.get(configuration.news_api_url, params=parameters)
            all_lists.append(response.json()["lists"])

        for existing_list in all_lists:
            all_news_data.append(existing_list)
    else:
        parameters = {
            "page": 1,
            "id": f"search:{quote(search_term)}",
            "channelId": 2,
            "type": "searchword",
        }
        response = requests.get(configuration.news_api_url, params=parameters)

        all_news_data = response.json()["lists"]
    return all_news_data

def get_new(db:Session, is_initial=False):
    """
    get new info

    :param is_initial:
    :return:
    """
    news_data = _get_new_info("價格", is_initial=is_initial)
    for news in news_data:
        relevance = _ask_openAI(
            system_prompt="你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
            user_prompt = news["title"]
        )
        if relevance == "high":
            response = requests.get(news["titleLink"])
            detailed_news = utils.parse_news_html(response.text)
            detailed_news["url"] = news["titleLink"]
            summary = summarize_news(detailed_news["content"])
            detailed_news["summary"] = summary["影響"]
            detailed_news["reason"] = summary["原因"]
            _add_new(detailed_news, db)

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
    keywords = _extract_search_keywords(prompt)
    # should change into simple factory pattern
    news_snapshots = _get_new_info(keywords, is_initial=False)
    for snapshot in news_snapshots:
        try:
            response = requests.get(snapshot["titleLink"])
            news = utils.parse_news_html(response.text)
            news["id"] = _generate_news_id()
            news_list.append(news)
        except Exception as exception:
            print(exception)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)
