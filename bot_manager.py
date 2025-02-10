import os
import discord
from dotenv import load_dotenv
from openai import OpenAI
from bot import Bot

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを環境変数から取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openAiClient = OpenAI(api_key=OPENAI_API_KEY)

class BotManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.token = os.getenv(f'DISCORD_{bot.mbti_type}_TOKEN')

        # Intentsを設定
        intents = discord.Intents.default()
        intents.messages = True  # メッセージの監視を許可

        # Discordクライアントの作成（intentsを指定）
        self.client = discord.Client(intents=intents)

    def setup_events(self):
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')

        @self.client.event
        async def on_message(message):
            # 自分のBotのメッセージには反応しない
            if message.author == self.client.user:
                return

            # メンションされた場合に反応
            if self.client.user.mentioned_in(message):
                user_message = message.content.replace(f'<@!{self.client.user.id}>', '').strip()

                # キャラのプロンプトを読み込む
                with open(f'mbti-prompt/{self.bot.mbti_file_name}.txt', 'r', encoding='utf-8') as file:
                    mbti_prompt = file.read()

                if user_message:
                    # OpenAIにメッセージを送信して返答を取得
                    # ref: https://platform.openai.com/docs/guides/text%EF%BC%8Dgeneration
                    completion = openAiClient.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "developer", "content": mbti_prompt},
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

    async def start(self):
        await self.client.start(self.token)

async def start_bot(bot: Bot):
    bot_manager = BotManager(bot)
    bot_manager.setup_events()
    await bot_manager.start()