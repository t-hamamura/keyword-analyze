import requests
from typing import Dict, Any, Optional
from app.config import get_settings
from app.utils.logger import logger

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
            }

            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Zenserp API request successful for keyword: {keyword}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Zenserp API request failed: {str(e)}")
            raise

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

        # 通常の検索結果
        if "organic" in search_result:
            for result in search_result["organic"]:
                extracted_data["organic_results"].append({
                    "title": result.get("title", ""),
                    "description": result.get("description", ""),
                    "url": result.get("link", "")
                })

        # サジェスト検索
        if "suggested_searches" in search_result:
            extracted_data["suggested_searches"] = search_result["suggested_searches"]

        # 関連検索
        if "related_searches" in search_result:
            extracted_data["related_searches"] = search_result["related_searches"]

        # バーティカル検索
        if "vertical_searches" in search_result:
            extracted_data["vertical_searches"] = search_result["vertical_searches"]

        # 関連する質問
        if "related_questions" in search_result:
            extracted_data["related_questions"] = search_result["related_questions"]

        # 動画
        if "videos" in search_result:
            for video in search_result["videos"]:
                extracted_data["videos"].append({
                    "title": video.get("title", ""),
                    "description": video.get("description", ""),
                    "url": video.get("link", "")
                })

        # 広告
        if "ads" in search_result:
            for ad in search_result["ads"]:
                extracted_data["ads"].append({
                    "title": ad.get("title", ""),
                    "description": ad.get("description", ""),
                    "url": ad.get("link", "")
                })

        # リッチリザルト
        if "rich_results" in search_result:
            extracted_data["rich_results"] = search_result["rich_results"]

        # ナレッジパネル
        if "knowledge_panel" in search_result:
            extracted_data["knowledge_panel"] = search_result["knowledge_panel"]

        # ローカルパック
        if "local_pack" in search_result:
            extracted_data["local_pack"] = search_result["local_pack"]

        # 強調スニペット
        if "featured_snippets" in search_result:
            extracted_data["featured_snippets"] = search_result["featured_snippets"]

        return extracted_data 