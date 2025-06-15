from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage
from app.config import get_settings
from app.utils.logger import logger
from app.services.zenserp_service import ZenserpService
from app.services.sheets_service import SheetsService

settings = get_settings()

class LineHandler:
    """LINE Messaging APIのハンドラークラス"""

    def __init__(self):
        self.line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
        self.zenserp_service = ZenserpService()
        self.sheets_service = SheetsService()

    def handle_webhook(self, body: str, signature: str) -> None:
        """
        Webhookリクエストを処理する

        Args:
            body (str): リクエストボディ
            signature (str): リクエストの署名
        """
        try:
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("Invalid signature")
            raise

    def handle_message(self, event) -> None:
        """
        メッセージイベントを処理する

        Args:
            event: LINE Messaging APIのイベントオブジェクト
        """
        try:
            # テキストメッセージの場合のみ処理
            if event.type != "message" or event.message.type != "text":
                return

            # キーワードを取得
            keyword = event.message.text

            # 検索を実行
            search_result = self.zenserp_service.search(keyword)
            search_data = self.zenserp_service.extract_search_data(search_result)

            # スプレッドシートに書き込み
            spreadsheet_url = self.sheets_service.write_search_results(keyword, search_data)

            # 結果をLINEに返信
            reply_message = f"検索結果を記録しました。\nスプレッドシートのURL: {spreadsheet_url}"
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_message)
            )

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            # エラーメッセージを返信
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="申し訳ありません。エラーが発生しました。")
            ) 