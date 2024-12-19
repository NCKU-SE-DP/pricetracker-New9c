import os
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file_path = os.path.join(os.path.dirname(__file__), "../.env")

class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file_path, extra="ignore")
    news_api_url: str = "https://udn.com/api/more"
    open_ai_api_key  : str
    open_ai_model    : str = "gpt-3.5-turbo"
    anthropic_api_key  : str
    anthropic_model    : str = "claude-3-5-sonnet-20240620"
configuration = Configuration()
