import discord
import asyncio
from src.services.config_service import ConfigService
from src.services.discord_client_setup import setup_discord_client

class TaskumaBot:
    """Tasukumaの機能を管理するクラス"""
    def __init__(self):
        self.client = setup_discord_client()
        self.config = ConfigService()
        self.token = self.config.get_discord_token("TASUKUMA")
        self.tasks = {}  # user_id: [tasks]

    def initialize_event_handlers(self):
        """イベントハンドラーの初期化"""
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            
            # TODO: タスク管理コマンドの処理

    async def start(self):
        """Botを起動する"""
        self.initialize_event_handlers()
        await self.client.start(self.token)

async def run_tasukuma():
    """Tasukumaを起動する"""
    bot = TaskumaBot()
    await bot.start()
