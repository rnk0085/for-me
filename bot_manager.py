import re
import discord
import random
from openai import OpenAI
from bot import Bot
from reactions import Reactions
from config import OPENAI_API_KEY, get_discord_token

openAiClient = OpenAI(api_key=OPENAI_API_KEY)

class BotManager:
    def __init__(self, bot: Bot, reactions: Reactions):
        self.bot = bot
        self.token = get_discord_token(bot.mbti_type)

        # Intentsを設定
        intents = discord.Intents.default()
        intents.messages = True  # メッセージの監視を許可
        # ref: https://discordpy.readthedocs.io/ja/latest/api.html#discord.Message.content
        intents.message_content = True

        # Discordクライアントの作成（intentsを指定）
        self.client = discord.Client(intents=intents)

        self.reactions = reactions

    def setup_events(self):
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')

        @self.client.event
        async def on_message(message):
            # 自分のBotのメッセージには反応しない
            if message.author == self.client.user:
                return
            
            # リアクション用の処理を走らせる（すでにリアクションが決定していたらスキップ）
            # メッセージに対して適切なリアクションを返す
            print(f"message.content = {message.content}")
            if message.content.strip():
                print("self.reactions.fetchReaction start")
                await self.reactions.fetchReaction(message_id=message.id, message_content=message.content)
                print("self.reactions.fetchReaction finished")
                reactions = self.reactions.getReactions(message.id)
                print(f"reactions = {reactions}")
                print("self.reactions.getReactions finished")


                # リアクションを付ける
                for reaction in reactions:
                    try:
                        # 50%でリアクションを付ける
                        if random.random() <= 0.5:
                            await message.add_reaction(reaction)
                    except Exception as e:
                        print(e)
            
            # ロールメンションの対応
            roles = message.role_mentions
            is_role_mentioned = False

            for role in roles:
                if self.client.user in role.members:
                    is_role_mentioned = True

            # メンションされた場合に反応
            if self.client.user.mentioned_in(message) or is_role_mentioned:
                # 正規表現を使って、ユーザーID、ユーザー名、ロールのメンションを削除
                user_message = re.sub(r'<@!?(\d+)>|<@!?(\w+)>|<@&(\d+)>', '', message.content).strip()


                # キャラのプロンプトを読み込む
                with open(f'prompt/mbti/{self.bot.mbti_file_name}.txt', 'r', encoding='utf-8') as file:
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

async def start_bot(bot: Bot, reactions: Reactions):
    bot_manager = BotManager(bot, reactions)
    bot_manager.setup_events()
    await bot_manager.start()