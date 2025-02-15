import discord
from src.services.discord_message_handler import DiscordMessageHandler
from src.services.periodic_message_service import PeriodicMessageService
from src.services.reaction_handler import ReactionHandler
from src.services.openai_client import OpenAIClient
from src.services.config_service import ConfigService
from src.services.discord_client_setup import setup_discord_client
from src.models.bot import Bot
from discord.ext import tasks

class DiscordBotManager:
    """Discordボットの初期化とイベント管理を行うクラス"""
    def __init__(
        self,
        bot: Bot,
        discord_client: discord.Client,
        message_handler: DiscordMessageHandler,
        periodic_message_service: PeriodicMessageService,
    ):
        self.bot = bot
        self.client = discord_client
        self.message_handler = message_handler
        self.periodic_message_service = periodic_message_service
        self.token = ConfigService().get_discord_token(bot.mbti_type)

    def initialize_event_handlers(self):
        """Discordイベントハンドラーの初期化"""
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')
            self.schedule_periodic_messages.start()

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            
            await self.message_handler.process_reactions(message)
            await self.message_handler.process_auto_response(message)
            await self.message_handler.process_mentions(message, self.client)

    @tasks.loop(minutes=1)
    async def schedule_periodic_messages(self):
        """定期的なメッセージ送信のスケジューリング"""
        try:
            print("定期的なメッセージ送信をスケジューリングしました")
            await self.periodic_message_service.send_random_message(self.client)
        except Exception as e:
            print(f"定期メッセージ送信中にエラーが発生しました: {e}")

    async def start(self):
        self.initialize_event_handlers()
        await self.client.start(self.token)

async def start_bot(bot: Bot, reactions: ReactionHandler):
    bot_manager = DiscordBotManager(
        bot=bot,
        discord_client=setup_discord_client(),
        message_handler=DiscordMessageHandler(bot, reactions, OpenAIClient(ConfigService()), ConfigService()),
        periodic_message_service=PeriodicMessageService(bot, OpenAIClient(ConfigService()), ConfigService()),
    )
    await bot_manager.start()