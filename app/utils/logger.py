import logging
from app.config import get_settings

settings = get_settings()

def setup_logger():
    """ロガーの設定を行う"""
    logger = logging.getLogger("keyword_analyze")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # フォーマッタの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # ハンドラの追加
    logger.addHandler(console_handler)

    return logger

# ロガーのインスタンスを作成
logger = setup_logger() 