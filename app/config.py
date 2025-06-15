from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

class Settings(BaseSettings):
    # LINE Messaging API設定
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str

    # Zenserp API設定
    ZENSERP_API_KEY: str

    # Google Sheets設定
    GOOGLE_SHEETS_CREDENTIALS_FILE: str
    GOOGLE_SHEETS_SPREADSHEET_ID: str

    # アプリケーション設定
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 