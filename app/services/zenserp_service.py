import requests
from typing import Dict, Any, Optional
from app.config import get_settings
from app.utils.logger import logger
import time

settings = get_settings()

class ZenserpService:
    """Zenserp APIを使用してGoogle検索結果を取得するサービスクラス"""

    def __init__(self):
        self.api_key = settings.ZENSERP_API_KEY
        self.base_url = "https://app.zenserp.com/api/v2/search"
        self.headers = {
            "apikey": self.api_key
        }

    def search(self, keyword: str) -> Dict[str, Any]:
        """
        Google検索を実行し、結果を取得する

        Args:
            keyword (str): 検索キーワード

        Returns:
            Dict[str, Any]: 検索結果
        """
        try:
            params = {
                "q": keyword,
                "gl": "jp",  # 日本向けの検索結果
                "hl": "ja",  # 日本語の結果
                "num": 20,   # 20件の結果を取得
                "device": "desktop",  # デスクトップ版の結果
            }

            logger.info(f"Starting Zenserp API request for keyword: {keyword}")
            
            # レート制限を考慮して少し待機
            time.sleep(1)
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30  # 30秒タイムアウト
            )
            
            # HTTPエラーチェック
            response.raise_for_status()

            data = response.json()
            
            # APIレスポンスの基本チェック
            if "error" in data:
                raise Exception(f"Zenserp API error: {data['error']}")
            
            logger.info(f"Zenserp API request successful for keyword: {keyword}")
            logger.debug(f"Response keys: {list(data.keys())}")
            
            return data

        except requests.exceptions.Timeout:
            logger.error(f"Zenserp API request timeout for keyword: {keyword}")
            raise Exception("検索APIのタイムアウトが発生しました。しばらく経ってから再度お試しください。")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Zenserp API authentication failed")
                raise Exception("API認証に失敗しました。APIキーを確認してください。")
            elif e.response.status_code == 429:
                logger.error("Zenserp API rate limit exceeded")
                raise Exception("API利用制限に達しました。しばらく経ってから再度お試しください。")
            else:
                logger.error(f"Zenserp API HTTP error: {e}")
                raise Exception(f"検索APIでエラーが発生しました: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Zenserp API request failed: {str(e)}")
            raise Exception("検索APIへの接続に失敗しました。ネットワーク接続を確認してください。")

    def extract_search_data(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        検索結果から必要なデータを抽出する

        Args:
            search_result (Dict[str, Any]): Zenserp APIの検索結果

        Returns:
            Dict[str, Any]: 抽出されたデータ
        """
        extracted_data = {
            "organic_results": [],
            "suggested_searches": [],
            "related_searches": [],
            "vertical_searches": [],
            "related_questions": [],
            "videos": [],
            "ads": [],
            "rich_results": [],
            "knowledge_panel": None,
            "local_pack": None,
            "featured_snippets": []
        }

        try:
            # 通常の検索結果
            if "organic" in search_result and isinstance(search_result["organic"], list):
                for result in search_result["organic"]:
                    extracted_data["organic_results"].append({
                        "title": self._safe_get(result, "title"),
                        "description": self._safe_get(result, "description"),
                        "url": self._safe_get(result, "link")
                    })

            # サジェスト検索
            if "suggested_searches" in search_result and isinstance(search_result["suggested_searches"], list):
                extracted_data["suggested_searches"] = [
                    item.get("query", "") if isinstance(item, dict) else str(item)
                    for item in search_result["suggested_searches"]
                ]

            # 関連検索
            if "related_searches" in search_result and isinstance(search_result["related_searches"], list):
                extracted_data["related_searches"] = [
                    item.get("query", "") if isinstance(item, dict) else str(item)
                    for item in search_result["related_searches"]
                ]

            # 関連する質問
            if "people_also_ask" in search_result and isinstance(search_result["people_also_ask"], list):
                extracted_data["related_questions"] = [
                    item.get("question", "") if isinstance(item, dict) else str(item)
                    for item in search_result["people_also_ask"]
                ]

            # 動画
            if "videos" in search_result and isinstance(search_result["videos"], list):
                for video in search_result["videos"]:
                    extracted_data["videos"].append({
                        "title": self._safe_get(video, "title"),
                        "description": self._safe_get(video, "description"),
                        "url": self._safe_get(video, "link")
                    })

            # 広告
            if "ads" in search_result and isinstance(search_result["ads"], list):
                for ad in search_result["ads"]:
                    extracted_data["ads"].append({
                        "title": self._safe_get(ad, "title"),
                        "description": self._safe_get(ad, "description"),
                        "url": self._safe_get(ad, "link")
                    })

            # その他のデータも安全に抽出
            for key in ["rich_results", "knowledge_panel", "local_pack", "featured_snippets"]:
                if key in search_result:
                    extracted_data[key] = search_result[key]

            logger.info(f"Extracted data: {len(extracted_data['organic_results'])} organic results, "
                       f"{len(extracted_data['videos'])} videos, {len(extracted_data['ads'])} ads")

        except Exception as e:
            logger.error(f"Error extracting search data: {str(e)}")
            # エラーが発生してもデータ抽出は続行

        return extracted_data

    def _safe_get(self, data: Dict[str, Any], key: str, default: str = "") -> str:
        """安全にディクショナリから値を取得する"""
        try:
            value = data.get(key, default)
            return str(value) if value is not None else default
        except:
            return default
