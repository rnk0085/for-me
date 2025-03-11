import discord
from discord.ext import commands

def setup_discord_client():
    """Discordクライアントを作成する"""
    intents = discord.Intents.default()
    intents.messages = True  # メッセージの監視を許可
    # ref: https://discordpy.readthedocs.io/ja/latest/api.html#discord.Message.content    
    intents.message_content = True  # メッセージ内容の監視を許可

    client = discord.Client(intents=intents)
    return client

def setup_tasukuma_bot():
    """TasukumaのDiscordクライアントを作成する"""
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.voice_states = True  # ボイスチャンネルの状態を取得

    bot = commands.Bot(command_prefix='!', intents=intents)
    return bot
