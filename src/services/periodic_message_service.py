import math
import random
import datetime
from src.models.bot import Bot
from src.services.openai_client import OpenAIClient
from src.services.config_service import ConfigService
from src.services.prompt_loader import get_prompt
from src.utils.random_utils import random_true_with_probability

class PeriodicMessageService:
    """定期的なメッセージ送信を管理するクラス"""
    def __init__(
        self,
        bot: Bot,
        openai_client: OpenAIClient,
        config_service: ConfigService
    ):
        self.bot = bot
        self.openai_client = openai_client
        self.config_service = config_service

    async def send_random_message(self, client):
        """キャラがランダムな雑談メッセージを送る"""
        if not self._should_send_message():
            print("雑談を自動投稿しない")
            return

        times_channel = self._get_target_channel(client)
        
        if times_channel:
            random_theme = random.choice(self.bot.interests)
            message = await self._generate_random_message(random_theme)
            await times_channel.send(message)

    def _get_target_channel(self, client):
        """投稿先チャンネルの取得"""
        return client.get_channel(
            self.config_service.get_channel_id(f"TIMES_{self.bot.mbti_type}")
        )

    async def _generate_random_message(self, random_theme: str) -> str:
        """ランダムな雑談メッセージを生成する"""
        prompt = get_prompt(f"prompt/mbti/{self.bot.mbti_file_name}.txt")
        return await self.openai_client.get_response(
            prompt=prompt,
            user_message=f"「{random_theme}」をテーマに自由に雑談して",
        )

    def _should_send_message(self) -> bool:
        """時間帯ごとに異なる確率で投稿する"""
        current_hour = datetime.datetime.now().hour
        rate = self._get_hourly_post_rate(current_hour)
        return random_true_with_probability(rate)

    def _get_hourly_post_rate(self, hour: int) -> float:
        """時間帯ごとの投稿確率を取得"""
        rates = {
            (7, 9): self._get_rate_for_all_characters(5),    # 朝: 5%
            (9, 12): self._get_rate_for_all_characters(20),   # 午前: 20%
            (12, 17): self._get_rate_for_all_characters(15),  # 午後: 15%
            (17, 20): self._get_rate_for_all_characters(10),  # 夕方: 10%
            (20, 24): self._get_rate_for_all_characters(5),  # 夜: 5%
        }
        
        for (start, end), rate in rates.items():
            if start <= hour < end:
                return rate
        return 0.0
    
    def _get_rate_for_all_characters(self, percent: int) -> float:
        """9キャラ全員のうち、1時間あたり percent の確率で少なくとも1回自動投稿される"""
        return 1 - 10 ** (math.log10(1 - percent / 100) / (9 * 60))
