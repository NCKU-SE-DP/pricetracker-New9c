from datetime import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

_env_file_path = os.path.join(os.path.dirname(__file__), "../.env")

class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file_path, env_prefix="USER_", extra="ignore")
    
    access_token_algorithm     : str        = "HS256"
    access_token_secret_key    : str        = "1892dhianiandowqd0n"
    access_token_url           : str        = "/api/v1/users/login"
    access_token_valid_duration: timedelta  = timedelta(minutes=30)
    password_hashing_algorithm : str        = "bcrypt"

configuration = Configuration()
