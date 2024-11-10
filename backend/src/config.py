from pydantic_settings import BaseSettings, SettingsConfigDict

import os
_env_file_path = os.path.join(os.path.dirname(__file__), ".env")
class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file_path, extra="ignore")
    cors_allow_credentials     : bool       = True
    cors_allow_headers         : tuple[str] = ("*",)
    cors_allow_methods         : tuple[str] = ("*",)
    cors_allow_origins         : tuple[str] = ("http://localhost:8080",)
    database_url               : str        = "sqlite:///news_database.db"
    sentry_dsn                 : str        = "https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000"
    sentry_traces_sample_rate  : float      = 1.0
    sentry_profiles_sample_rate: float      = 1.0
configuration = Configuration()
