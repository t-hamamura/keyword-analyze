from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.line.handler import LineHandler
from app.utils.logger import logger
import traceback

# FastAPIアプリケーションの設定
app = FastAPI(
    title="Keyword Analyze API",
    description="LINE Messaging API、Zenserp API、Google Sheetsを使用したキーワード分析ツール",
    version="1.0.0"
)

# グローバルなハンドラーインスタンス
line_handler = None

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    global line_handler
    try:
        line_handler = LineHandler()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

@app.post("/webhook")
async def webhook(request: Request):
    """
    LINE Messaging APIのWebhookエンドポイント
    """
    try:
        # リクエストボディを取得
        body = await request.body()
        signature = request.headers.get("X-Line-Signature", "")

        if not signature:
            logger.warning("Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")

        # Webhookを処理
        if line_handler is None:
            raise HTTPException(status_code=500, detail="Handler not initialized")
            
        line_handler.handle_webhook(body.decode(), signature)

        return JSONResponse(content={"status": "success"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """
    ヘルスチェックエンドポイント
    """
    return {
        "status": "ok", 
        "message": "Keyword Analyze API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """
    詳細なヘルスチェックエンドポイント
    """
    try:
        # 各コンポーネントの状態確認
        health_status = {
            "status": "healthy",
            "components": {
                "line_handler": line_handler is not None,
                "zenserp_service": True,  # 実際のAPI呼び出しは避ける
                "sheets_service": True    # 実際のAPI呼び出しは避ける
            }
        }
        
        # いずれかのコンポーネントが失敗している場合
        if not all(health_status["components"].values()):
            health_status["status"] = "unhealthy"
            
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy", 
            "error": str(e)
        }
