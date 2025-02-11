import re
import random
from bot import Bot
from reaction_handler import ReactionHandler
from config import get_discord_token, get_channel_id, REACTION_RATE, AUTO_REPLY_RATE, AUTO_REPLY_IN_FREE_TALK_RATE
from openai_client import OpenAIClient
from role_mention_checker import check_role_mention
from discord_client_setup import setup_discord_client
from prompt_loader import get_prompt

class BotManager:
    def __init__(self, bot: Bot, reactions: ReactionHandler):
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
            
            await self.handle_reactions(message)
            await self.handle_auto_response(message)
            await self.handle_mentions(message)
            
    
    async def handle_reactions(self, message):
        """メッセージに対して適切なリアクションを付ける"""
        if message.content.strip():
            if "times" in message.channel.name:
                print("timesにはリアクションを付けない")
                return
            
            if str(message.channel.id) == get_channel_id("DEV"):
                print("開発用のチャンネルにはリアクションを付けない")
                return
            
            if message.author.bot:
                if random.random() <= REACTION_RATE:
                    print("Botにはランダムでリアクションを付ける")
                    return

            await self.reactions.fetchReaction(message_id=message.id, message_content=message.content)
            reactions = self.reactions.getReactions(message.id)

            # リアクションを付ける
            for reaction in reactions:
                if random.random() <= REACTION_RATE:
                    try:
                        await message.add_reaction(reaction)
                    except Exception as e:
                        print(f"Error = {e}: リアクションが送れませんでした")

    async def handle_auto_response(self, message):
        """メンションが無い場合に自動で返信する"""
        # 自動返信対象かどうかをチェックする
        # 自動返信対象＝フリートーク、FB、ほめる
        channel_id = message.channel.id
        free_talk_channel_id = get_channel_id("FREE_TALK")
        fb_channel_id = get_channel_id("FB")
        praise_channel_id = get_channel_id("PRAISE")

        is_free_talk = str(channel_id) == free_talk_channel_id
        is_fb = str(channel_id) == fb_channel_id
        is_praise = str(channel_id) == praise_channel_id

        print(f"is_free_talk = {is_free_talk}")
        print(f"is_fb = {is_fb}")
        print(f"is_praise = {is_praise}")

        if not is_free_talk and not is_fb and not is_praise:
            print("「フリートーク、FB、ほめる」以外は自動返信をしない")
            return

        # Botかどうかをチェックする。フリートーク以外はBot同士で会話をしない。
        if message.author.bot and is_fb:
            print("Botに対してFBはしない")
            return

        if message.author.bot and is_praise:
            print("Botに対して褒めない")
            return

        # 確率で返信させる
        if is_free_talk and random.random() > AUTO_REPLY_IN_FREE_TALK_RATE:
            print("フリートークは高確率で返信しない")
            return
        if is_fb and random.random() > AUTO_REPLY_RATE:
            print("FBは低確率で返信しない")
            return
        if is_praise and random.random() > AUTO_REPLY_RATE:
            print("ほめるは低確率で返信しない")
            return
        
        pre_prompt = ""
        if is_free_talk:
            pre_prompt = "あなたが興味関心のある話題をテーマに雑談してください。"
        if is_fb:
            pre_prompt = "フィードバックをしてください。また、"
        if is_praise:
            pre_prompt = "全力で褒めてください。また、"

        mbti_prompt = get_prompt(f'prompt/mbti/{self.bot.mbti_file_name}.txt')

        response = self.openai_client.get_response(
            prompt = pre_prompt + mbti_prompt,
            user_message = message.content,
        )

        await message.channel.send(response)

    async def handle_mentions(self, message):
        """メンションがあった場合にキャラが返信をする"""
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

async def start_bot(bot: Bot, reactions: ReactionHandler):
    bot_manager = BotManager(bot, reactions)
    bot_manager.setup_events()
    await bot_manager.start()