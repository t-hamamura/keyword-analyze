import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Dict, Any, List
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

class SheetsService:
    """Google Sheets APIを使用してデータを記録するサービスクラス"""

    def __init__(self):
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.client = self._get_client()

    def _get_client(self) -> gspread.Client:
        """Google Sheets APIクライアントを取得する"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, scope
        )
        return gspread.authorize(credentials)

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
            
            # 新しいシートを作成（キーワード名をシート名として使用）
            sheet = spreadsheet.add_worksheet(
                title=keyword,
                rows=1000,
                cols=20
            )

            # データを書き込む
            self._write_data_to_sheet(sheet, keyword, search_data)

            # スプレッドシートのURLを返す
            return spreadsheet.url

        except Exception as e:
            logger.error(f"Failed to write to Google Sheets: {str(e)}")
            raise

    def _write_data_to_sheet(self, sheet: gspread.Worksheet, keyword: str, data: Dict[str, Any]):
        """
        シートにデータを書き込む

        Args:
            sheet (gspread.Worksheet): 書き込み先のシート
            keyword (str): 検索キーワード
            data (Dict[str, Any]): 書き込むデータ
        """
        # ヘッダー行を書き込む
        headers = [
            "検索キーワード",
            "サジェストキーワード",
            "関連検索キーワード",
            "バーティカル検索キーワード",
            "関連する質問",
            "検索結果タイトル",
            "検索結果ディスクリプション",
            "検索結果URL",
            "動画タイトル",
            "動画ディスクリプション",
            "動画URL",
            "広告タイトル",
            "広告ディスクリプション",
            "広告URL",
            "リッチリザルト",
            "ナレッジパネル",
            "ローカルパック",
            "強調スニペット"
        ]
        sheet.append_row(headers)

        # 検索結果を書き込む
        row_data = [
            keyword,
            "\n".join(data.get("suggested_searches", [])),
            "\n".join(data.get("related_searches", [])),
            "\n".join(data.get("vertical_searches", [])),
            "\n".join(data.get("related_questions", [])),
        ]

        # 通常の検索結果
        organic_results = data.get("organic_results", [])
        for result in organic_results:
            row_data.extend([
                result.get("title", ""),
                result.get("description", ""),
                result.get("url", "")
            ])

        # 動画
        videos = data.get("videos", [])
        for video in videos:
            row_data.extend([
                video.get("title", ""),
                video.get("description", ""),
                video.get("url", "")
            ])

        # 広告
        ads = data.get("ads", [])
        for ad in ads:
            row_data.extend([
                ad.get("title", ""),
                ad.get("description", ""),
                ad.get("url", "")
            ])

        # その他のデータ
        row_data.extend([
            str(data.get("rich_results", [])),
            str(data.get("knowledge_panel", "")),
            str(data.get("local_pack", "")),
            str(data.get("featured_snippets", []))
        ])

        # データを書き込む
        sheet.append_row(row_data) 