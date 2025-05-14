from pydantic_settings import BaseSettings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
ENV_PATH = BASE_DIR.parent               # project_root/.env


class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ENV_PATH / ".env"


settings = Settings()