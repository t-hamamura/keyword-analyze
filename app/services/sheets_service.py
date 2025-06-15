import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Any, List
from app.config import get_settings
from app.utils.logger import logger
import datetime
import os

settings = get_settings()

class SheetsService:
    """Google Sheets APIを使用してデータを記録するサービスクラス"""

    def __init__(self):
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.client = self._get_client()

    def _get_client(self) -> gspread.Client:
        """Google Sheets APIクライアントを取得する"""
        try:
            # 認証ファイルの存在確認
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(f"Google Sheets credentials file not found: {self.credentials_file}")
            
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            client = gspread.authorize(credentials)
            logger.info("Google Sheets client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {str(e)}")
            raise

    def write_search_results(self, keyword: str, search_data: Dict[str, Any]) -> str:
        """
        検索結果をスプレッドシートに書き込む

        Args:
            keyword (str): 検索キーワード
            search_data (Dict[str, Any]): 検索結果データ

        Returns:
            str: スプレッドシートのURL
        """
        try:
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            # タイムスタンプ付きのシート名を作成
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            sheet_name = f"{keyword}_{timestamp}"[:31]  # Googleシートのシート名は31文字制限
            
            try:
                # 新しいシートを作成
                sheet = spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=10
                )
            except Exception as e:
                # シート作成に失敗した場合は、既存のシートを使用
                logger.warning(f"Failed to create new sheet, using first sheet: {str(e)}")
                sheet = spreadsheet.sheet1

            # データを書き込む
            self._write_data_to_sheet(sheet, keyword, search_data)

            # スプレッドシートのURLを返す
            logger.info(f"Successfully wrote data to Google Sheets for keyword: {keyword}")
            return spreadsheet.url

        except Exception as e:
            logger.error(f"Failed to write to Google Sheets: {str(e)}")
            raise

    def _write_data_to_sheet(self, sheet: gspread.Worksheet, keyword: str, data: Dict[str, Any]):
        """
        シートにデータを書き込む（行ベースで整理）

        Args:
            sheet (gspread.Worksheet): 書き込み先のシート
            keyword (str): 検索キーワード
            data (Dict[str, Any]): 書き込むデータ
        """
        try:
            # シートをクリア
            sheet.clear()
            
            # ヘッダー行を書き込む
            headers = [
                "検索キーワード", "データ種別", "タイトル", "説明", "URL", "その他情報"
            ]
            sheet.append_row(headers)

            # 検索キーワード基本情報
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([keyword, "基本情報", "", "", "", f"検索実行日時: {timestamp}"])

            # サジェスト検索
            suggestions = data.get("suggested_searches", [])
            if suggestions:
                for suggestion in suggestions[:10]:  # 最大10件
                    sheet.append_row([keyword, "サジェスト検索", suggestion, "", "", ""])

            # 関連検索
            related = data.get("related_searches", [])
            if related:
                for rel in related[:10]:  # 最大10件
                    sheet.append_row([keyword, "関連検索", rel, "", "", ""])

            # 通常の検索結果
            organic_results = data.get("organic_results", [])
            if organic_results:
                for result in organic_results[:20]:  # 最大20件
                    sheet.append_row([
                        keyword, 
                        "オーガニック検索結果", 
                        result.get("title", "")[:500],  # 500文字制限
                        result.get("description", "")[:500], 
                        result.get("url", ""), 
                        ""
                    ])

            # 動画
            videos = data.get("videos", [])
            if videos:
                for video in videos[:10]:  # 最大10件
                    sheet.append_row([
                        keyword, 
                        "動画", 
                        video.get("title", "")[:500], 
                        video.get("description", "")[:500], 
                        video.get("url", ""), 
                        ""
                    ])

            # 広告
            ads = data.get("ads", [])
            if ads:
                for ad in ads[:10]:  # 最大10件
                    sheet.append_row([
                        keyword, 
                        "広告", 
                        ad.get("title", "")[:500], 
                        ad.get("description", "")[:500], 
                        ad.get("url", ""), 
                        ""
                    ])

            logger.info(f"Successfully wrote {len(organic_results)} organic results, {len(videos)} videos, {len(ads)} ads to sheet")

        except Exception as e:
            logger.error(f"Error writing data to sheet: {str(e)}")
            # エラーが発生してもシステム全体を止めないよう、基本情報だけでも書き込む
            try:
                sheet.clear()
                sheet.append_row(["検索キーワード", "エラー情報", "タイムスタンプ"])
                sheet.append_row([keyword, str(e), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            except:
                pass
            raise
