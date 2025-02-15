import discord

def setup_discord_client():
    """Discordクライアントを作成する"""
    intents = discord.Intents.default()
    intents.messages = True  # メッセージの監視を許可
    # ref: https://discordpy.readthedocs.io/ja/latest/api.html#discord.Message.content    
    intents.message_content = True  # メッセージ内容の監視を許可

    client = discord.Client(intents=intents)
    return client
