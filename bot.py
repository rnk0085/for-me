import discord
from openai import OpenAI
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを環境変数から取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# DiscordのBotのTokenを環境変数から取得
DISCORD_ENTP_TOKEN = os.getenv('DISCORD_ENTP_TOKEN')

# Intentsを設定
intents = discord.Intents.default()
intents.messages = True  # メッセージの監視を許可

# Discordクライアントの作成（intentsを指定）
client = discord.Client(intents=intents)

openAiClient = OpenAI(api_key=OPENAI_API_KEY)

# メンションされたときに反応する処理
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # 自分のBotのメッセージには反応しない
    if message.author == client.user:
        return

    # メンションされた場合に反応
    if client.user.mentioned_in(message):
        user_message = message.content.replace(f'<@!{client.user.id}>', '').strip()

        if user_message:
            # OpenAIにメッセージを送信して返答を取得
            # ref: https://platform.openai.com/docs/guides/text%EF%BC%8Dgeneration
            completion = openAiClient.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "developer", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ]
            )

            print(f'completion = {completion}')

            # 生成された返答を送信
            await message.channel.send(completion.choices[0].message.content)
        else:
            await message.channel.send("Hello! How can I assist you today?")

# Botを実行
client.run(DISCORD_ENTP_TOKEN)
