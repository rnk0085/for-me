import random
import datetime
from src.models.bot import Bot
from src.services.openai_client import OpenAIClient
from src.services.config_service import ConfigService
from src.services.prompt_loader import get_prompt
from src.utils.random_utils import random_true_with_probability

class PeriodicMessageService:
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
        if not self._should_post():
            return

        times_channel = client.get_channel(
            self.config_service.get_channel_id(f"TIMES_{self.bot.mbti_type}")
        )
        
        if times_channel:
            random_theme = random.choice(self.bot.interests)
            message = await self._generate_random_message(random_theme)
            await times_channel.send(message)

    async def _generate_random_message(self, random_theme: str) -> str:
        """ランダムな雑談メッセージを生成する"""
        prompt = get_prompt(f"prompt/mbti/{self.bot.mbti_file_name}.txt")
        return self.openai_client.get_response(
            prompt=prompt,
            user_message=f"「{random_theme}」をテーマに自由に雑談して",
        )

    def _should_post(self) -> bool:
        """時間帯ごとに異なる確率で投稿する"""
        current_hour = datetime.datetime.now().hour
        rate = self._get_post_rate(current_hour)
        return random_true_with_probability(rate)

    def _get_post_rate(self, hour: int) -> float:
        if 7 <= hour < 9:
            return 0.01 * 0.57  # 5%
        elif 9 <= hour < 12:
            return 0.01 * 2.45  # 20%
        elif 12 <= hour < 17:
            return 0.01 * 1.79  # 15%
        elif 17 <= hour < 20:
            return 0.01 * 1.17  # 10%
        elif 20 <= hour <= 23:
            return 0.01 * 0.57  # 5%
        return 0 