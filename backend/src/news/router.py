from fastapi import APIRouter, HTTPException
from src.dependencies import DatabaseSession
from src.user.dependencies import CurrentLoggedInUser
from . import service
from .schemas import PromptRequest, NewsSumaryRequestSchema, NewsSummaryCustomModelRequestSchema
from .exceptions import InvalidAIModelException

import logging
from sentry_sdk import capture_exception

router = APIRouter(prefix="/api/v1/news")


@router.get("/news")
def read_news(db: DatabaseSession):
    logging.debug("Accessed /api/v1/news/news")
    return service.retrieve_news_with_upvote_status(db, None)


@router.get("/user_news")
def read_user_news(db: DatabaseSession, user: CurrentLoggedInUser):
    logging.debug("Accessed /api/v1/news/user_news")
    return service.retrieve_news_with_upvote_status(db, user)



@router.post("/search_news")
async def search_news(request: PromptRequest):
    logging.debug(f"Accessed /api/v1/news/search_news with prompt: {request.prompt}")
    return service.search_news(request.prompt)

@router.post("/news_summary")
async def news_summary(news: NewsSumaryRequestSchema, user: CurrentLoggedInUser):
    logging.debug("Accessed /api/v1/news/news_summary")
    try:
        summary = service.summarize_news(news.content)
    except InvalidAIModelException as e:
        logging.error("Invalid model used")
        capture_exception(e)
        return HTTPException(status_code=400, detail="Passed in invalid LLM model")
    response = {}
    if summary:
        response["summary"] = summary["影響"]
        response["reason"] = summary["原因"]
    return response

@router.post("/news_summary_custom_model")
async def summarize_news_with_custom_model(schema: NewsSummaryCustomModelRequestSchema):
    try:
        summary = service.summarize_news(schema.content, schema.llm_model)
    except InvalidAIModelException as e:
        logging.error("Invalid model used")
        capture_exception(e)
        return HTTPException(status_code=400, detail="Passed in invalid LLM model")
    response = {}
    if summary:
        response["summary"] = summary["影響"]
        response["reason"] = summary["原因"]
    return response

@router.post("/{id}/upvote")
def upvote_article(
        id,
        db: DatabaseSession,
        user: CurrentLoggedInUser,
):
    logging.debug(f"Accessed /api/v1/news/{id}/upvote")
    message = service.toggle_upvote(id, user.id, db)
    return {"message": message}




