from fastapi import APIRouter
from src.dependencies import DatabaseSession
from src.user.dependencies import CurrentLoggedInUser
from . import service
from .schemas import PromptRequest, NewsSumaryRequestSchema

router = APIRouter(prefix="/api/v1/news")


@router.get("/news")
def read_news(db: DatabaseSession):
    return service.retrieve_news_with_upvote_status(db, None)


@router.get("/user_news")
def read_user_news(db: DatabaseSession, user: CurrentLoggedInUser):
    return service.retrieve_news_with_upvote_status(db, user)



@router.post("/search_news")
async def search_news(request: PromptRequest):
    return service.search_news(request.prompt)

@router.post("/news_summary")
async def news_summary( news: NewsSumaryRequestSchema, user: CurrentLoggedInUser):
    summary = service.summarize_news(news.content)
    response = {}
    response["summary"] = summary["影響"]
    response["reason"] = summary["原因"]
    return response


@router.post("/{id}/upvote")
def upvote_article(
        id,
        db: DatabaseSession,
        user: CurrentLoggedInUser,
):
    message = service.toggle_upvote(id, user.id, db)
    return {"message": message}




