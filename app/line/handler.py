from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
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
        
        # イベントハンドラーを登録
        self.handler.add(MessageEvent, message=TextMessage)(self.handle_message)

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
            # キーワードを取得
            keyword = event.message.text.strip()
            logger.info(f"Received keyword: {keyword}")

            if not keyword:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="キーワードを入力してください。")
                )
                return

            # 処理開始メッセージ
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"「{keyword}」の検索結果を取得中です。しばらくお待ちください...")
            )

            # 検索を実行
            search_result = self.zenserp_service.search(keyword)
            search_data = self.zenserp_service.extract_search_data(search_result)

            # スプレッドシートに書き込み
            spreadsheet_url = self.sheets_service.write_search_results(keyword, search_data)

            # 結果をLINEにプッシュメッセージで送信
            reply_message = f"✅ 検索結果を記録しました！\n\n🔍 キーワード: {keyword}\n📊 スプレッドシート: {spreadsheet_url}"
            
            # プッシュメッセージとして送信
            user_id = event.source.user_id
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=reply_message)
            )
            
            logger.info(f"Successfully processed keyword: {keyword}")

        except LineBotApiError as e:
            logger.error(f"LINE Bot API Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            # エラーメッセージを返信
            try:
                error_message = "❌ 申し訳ありません。処理中にエラーが発生しました。\n\n以下をご確認ください：\n・キーワードが正しく入力されているか\n・しばらく時間をおいてから再度お試しください"
                user_id = event.source.user_id
                self.line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text=error_message)
                )
            except Exception as push_error:
                logger.error(f"Failed to send error message: {str(push_error)}")
