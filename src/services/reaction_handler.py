import asyncio
from typing import List, Dict, Optional
from src.services.openai_client import OpenAIClient
from src.services.config_service import ConfigService
from src.services.prompt_loader import get_prompt

class ReactionHandler:
    """
    メッセージに対するリアクション（絵文字）を管理するクラス
    
    Attributes:
        reactions (Dict[str, List[str]]): メッセージIDとリアクションのマッピング
        fetching_message_ids (List[str]): 現在リアクション取得中のメッセージIDリスト
        openai_client (OpenAIClient): OpenAI APIクライアント
        reaction_genre_map (Dict[str, str]): ジャンルと絵文字のマッピング
    """

    # ジャンルと対応する絵文字のマッピング
    REACTION_GENRE_MAP = {
        "良い": "👍",
        "面白い": "😂",
        "悲しい": "😢",
        "怒り": "😡",
        "愛": "❤️",
        "驚き": "😲",
        "混乱": "🤔",
        "感謝": "🙏",
        "モチベーション": "💪",
        "お祝い": "🎊",
        "眠い": "💤",
        "仕事": "💼",
        "旅行": "✈️",
        "運動": "🏋️",
        "勉強": "📚",
    }

    def __init__(self, config_service: ConfigService):
        """
        ReactionHandlerの初期化

        Args:
            config_service (ConfigService): 設定サービス
        """
        self.reactions: Dict[str, List[str]] = {}
        self.fetching_message_ids: List[str] = []
        self.openai_client = OpenAIClient(config_service)

    async def fetch_reaction(self, message_id: str, message_content: str) -> None:
        """
        OpenAIを使用してメッセージに対するリアクションを取得する

        Args:
            message_id (str): メッセージID
            message_content (str): メッセージ内容
        """
        if message_id in self.fetching_message_ids:
            await asyncio.sleep(1)
            return

        if message_id not in self.reactions:
            self.fetching_message_ids.append(message_id)
            try:
                await self._process_reaction(message_id, message_content)
            finally:
                self.fetching_message_ids.remove(message_id)
                asyncio.create_task(self._remove_old_reactions(message_id))

    def get_reactions(self, message_id: str) -> List[str]:
        """
        メッセージIDに対応するリアクションを取得する

        Args:
            message_id (str): メッセージID

        Returns:
            List[str]: リアクションのリスト
        """
        return self.reactions.get(message_id, [])

    async def _process_reaction(self, message_id: str, message_content: str) -> None:
        """
        リアクションの処理を行う

        Args:
            message_id (str): メッセージID
            message_content (str): メッセージ内容
        """
        prompt = f"「{message_content}」{get_prompt('prompt/reaction.txt')}"
        genre_response = await self.openai_client.get_response(
            prompt=prompt,
            user_message=message_content,
        )

        recommend_reactions = self._generate_reactions(genre_response)
        self.reactions[message_id] = recommend_reactions

    def _generate_reactions(self, genre_response: str) -> List[str]:
        """
        ジャンルレスポンスからリアクションリストを生成する

        Args:
            genre_response (str): ジャンルレスポンス

        Returns:
            List[str]: リアクションのリスト
        """
        reactions = ["👀"]  # デフォルトリアクション
        try:
            for genre, emoji in self.REACTION_GENRE_MAP.items():
                if genre in genre_response:
                    reactions.append(emoji)
        except Exception as e:
            print(f"リアクション生成エラー: {e}")
        return reactions

    async def _remove_old_reactions(self, message_id: str, timeout: int = 60) -> None:
        """
        一定時間後にリアクションデータを削除する

        Args:
            message_id (str): メッセージID
            timeout (int, optional): タイムアウト時間（秒）. デフォルトは60秒.
        """
        await asyncio.sleep(timeout)
        if message_id in self.reactions:
            del self.reactions[message_id]
            print(f"メッセージID {message_id} のリアクションデータを削除しました")
