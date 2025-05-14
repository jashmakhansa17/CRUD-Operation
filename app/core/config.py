from pydantic_settings import BaseSettings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
ENV_PATH = BASE_DIR.parent               # project_root/.env

class Setting(BaseSettings):
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

settings = Setting()
