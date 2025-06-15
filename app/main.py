from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.line.handler import LineHandler
from app.utils.logger import logger

app = FastAPI(title="Keyword Analyze")
line_handler = LineHandler()

@app.post("/webhook")
async def webhook(request: Request):
    """
    LINE Messaging APIのWebhookエンドポイント
    """
    try:
        # リクエストボディを取得
        body = await request.body()
        signature = request.headers.get("X-Line-Signature", "")

        # Webhookを処理
        line_handler.handle_webhook(body.decode(), signature)

        return JSONResponse(content={"status": "success"})

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "ok", "message": "Keyword Analyze API is running"} 