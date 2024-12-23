import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, FastAPI
from .logger import init_logger
import logging
init_logger()
logging.debug("Initializing...")
import os

from .config import configuration
from .database import get_database, get_database_persist_changes_disabled
from .models import NewsArticle
from .user.router import router as user_api_router
from .news import service as news_service
from .news.router import router as news_api_router
from .price.router import router as price_api_router

# from pydantic import BaseModel

sentry_sdk.init(
    dsn=configuration.sentry_dsn,
    traces_sample_rate=configuration.sentry_traces_sample_rate,
    profiles_sample_rate=configuration.sentry_profiles_sample_rate,
    _experiments={"continuous_profiling_auto_start": True}
)

app = FastAPI()
scheduler = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=configuration.cors_allow_origins,
    allow_credentials=configuration.cors_allow_credentials,
    allow_methods=configuration.cors_allow_methods,
    allow_headers=configuration.cors_allow_headers,
)

import os


@app.on_event("startup")
def start_scheduler():
    db = get_database_persist_changes_disabled()
    if db.query(NewsArticle).count() == 0:
        # should change into simple factory pattern
        news_service.get_new(db)
    db.close()
    def job():
        database = get_database()
        news_service.get_new(db)
        database.close()
    scheduler.add_job(job, "interval", minutes=100)

    scheduler.start()
    logging.debug("Background scheduler started.")
    logging.info("PriceTracker backend has started.")


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    logging.debug("Background scheduler shut down.")



app.include_router(user_api_router)
app.include_router(news_api_router)
app.include_router(price_api_router)
