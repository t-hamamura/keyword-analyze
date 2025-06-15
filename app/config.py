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
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        required_vars = [
            'LINE_CHANNEL_ACCESS_TOKEN',
            'LINE_CHANNEL_SECRET', 
            'ZENSERP_API_KEY',
            'GOOGLE_SHEETS_CREDENTIALS_FILE',
            'GOOGLE_SHEETS_SPREADSHEET_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
