import discord
from discord.ext import commands
from src.services.config_service import ConfigService
from src.services.discord_client_setup import setup_tasukuma_bot

class TaskumaBot:
    """Tasukumaの機能を管理するクラス"""
    def __init__(self):
        self.bot = setup_tasukuma_bot()
        self.config = ConfigService()
        self.token = self.config.get_discord_token("TASUKUMA")

    def initialize_event_handlers(self):
        """イベントハンドラーの初期化"""
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user}')
            
            try:
                guild = discord.Object(id=self.config.get_guild_id())
                await self.bot.tree.sync(guild=guild)
                print(f"✅ コマンドが同期されました！")
            except Exception as e:
                print(f"🚨 コマンドの同期に失敗: {e}")
        
        @self.bot.hybrid_command(name="ping", description="Tasukumaが応答するか確認する")
        async def ping(ctx):
            await ctx.send("Pong!")
        
        @self.bot.hybrid_command(name="list_commands", description="登録済みのコマンドを確認する")
        async def list_commands(ctx):
            commands = [cmd.name for cmd in self.bot.tree.get_commands()]
            await ctx.send(f"登録されているコマンド: {commands}")

    async def start(self):
        """Botを起動する"""
        self.initialize_event_handlers()
        await self.bot.start(self.token)

async def run_tasukuma():
    """Tasukumaを起動する"""
    bot = TaskumaBot()
    await bot.start()
