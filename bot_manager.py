import re
import random
from bot import Bot
from reactions import Reactions
from config import get_discord_token, REACTION_RATE
from openai_client import OpenAIClient
from role_mention_checker import check_role_mention
from discord_client_setup import setup_discord_client
from prompt_loader import get_prompt

class BotManager:
    def __init__(self, bot: Bot, reactions: Reactions):
        self.bot = bot
        self.token = get_discord_token(bot.mbti_type)
        self.openai_client = OpenAIClient()
        self.client = setup_discord_client()
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
            
            # メッセージに対して適切なリアクションを返す
            if message.content.strip():
                await self.reactions.fetchReaction(message_id=message.id, message_content=message.content)
                reactions = self.reactions.getReactions(message.id)

                # リアクションを付ける
                for reaction in reactions:
                    if random.random() <= REACTION_RATE:
                        try:
                            await message.add_reaction(reaction)
                        except Exception as e:
                            print(f"Error = {e}: リアクションが送れませんでした")

            # メンションされた場合に反応
            if self.client.user.mentioned_in(message) or check_role_mention(message=message, client=self.client):
                # 正規表現を使って、ユーザーID、ユーザー名、ロールのメンションを削除
                user_message = re.sub(r'<@!?(\d+)>|<@!?(\w+)>|<@&(\d+)>', '', message.content).strip()

                # キャラのプロンプトを読み込む
                mbti_prompt = get_prompt(f'prompt/mbti/{self.bot.mbti_file_name}.txt')
                if user_message:
                    response = self.openai_client.get_response(
                        prompt = mbti_prompt,
                        user_message = user_message,
                    )

                    # 生成された返答を送信
                    await message.channel.send(response)

    async def start(self):
        await self.client.start(self.token)

async def start_bot(bot: Bot, reactions: Reactions):
    bot_manager = BotManager(bot, reactions)
    bot_manager.setup_events()
    await bot_manager.start()