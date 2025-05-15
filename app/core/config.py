from pydantic_settings import BaseSettings
import os
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # app/
ENV_PATH = BASE_DIR.parent               # project_root/.env

load_dotenv(dotenv_path=ENV_PATH)
class Environments(str, Enum):
    DEVELOPMENT = 'dev'
    STAGING = 'stage'
    PRODUCTION = 'prod'
    TESTING = 'test'

class Settings(BaseSettings):
    database_url: str  
    
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    
    email_host: str
    email_port: int
    email_username: str
    email_password: str
    
    email_expire_minutes: int
    
    blacklisted_token_expire_minutes: int
    class Config:
        env_file = ENV_PATH / ".env" 
        extra = 'allow'


class DevSettings(Settings):
    debug: bool = True
   

class ProdSettings(Settings):
    debug: bool = False

    class Config:
        env_file = ENV_PATH / ".env.prod"


class StageSettings(Settings):
    debug: bool = False

    class Config:
        env_file = ENV_PATH / ".env.stage"


def get_config():
    env = os.getenv("APP_ENV", "dev").lower()
    if env == Environments.DEVELOPMENT:
        return DevSettings()
    elif env == Environments.STAGING:
        return StageSettings()
    elif env == Environments.PRODUCTION:
        return ProdSettings()
    else:
        return Settings()  # default fallback


settings = get_config()
