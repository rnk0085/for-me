import discord
from discord import app_commands
from discord.ext import commands
from src.services.config_service import ConfigService

class TaskumaBot(commands.Bot):
    """Tasukumaの機能を管理するクラス"""
    def __init__(self):
        self.config = ConfigService()
        self.token = self.config.get_discord_token("TASUKUMA")
        
        # intentsを設定
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        intents.voice_states = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description='タスク管理Bot'
        )
    
    async def setup_hook(self):
        """Botの初期設定"""
        """Cog をロードしてスラッシュコマンドを同期"""
        await self.load_extension("src.cogs.general")

        guild = discord.Object(id=self.config.get_guild_id())
        await self.tree.sync(guild=guild)
        print("✅ コマンドを同期しました！")
    
    async def on_ready(self):
        """Bot起動時の処理"""
        print(f'Logged in as {self.user}')

async def run_tasukuma():
    """Tasukumaを起動する"""
    bot = TaskumaBot()
    await bot.start(bot.token)
