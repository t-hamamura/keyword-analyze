import logging
import sys
from app.config import get_settings

# 設定を取得（エラー時は默认値を使用）
try:
    settings = get_settings()
    log_level = settings.LOG_LEVEL
except:
    log_level = "INFO"

def setup_logger():
    """ロガーの設定を行う"""
    logger = logging.getLogger("keyword_analyze")
    
    # ログレベルの設定
    try:
        level = getattr(logging, log_level.upper())
    except AttributeError:
        level = logging.INFO
        
    logger.setLevel(level)

    # 既存のハンドラをクリア（重複を避けるため）
    logger.handlers.clear()

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # フォーマッタの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # ハンドラの追加
    logger.addHandler(console_handler)

    # 親ロガーへの伝播を防ぐ
    logger.propagate = False

    return logger

# ロガーのインスタンスを作成
logger = setup_logger()
