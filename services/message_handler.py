import re
from services.bot import Bot
from services.reaction_handler import ReactionHandler
from services.openai_client import OpenAIClient
from services.config_service import ConfigService
from services.custom_random import random_true_with_probability
from role_mention_checker import check_role_mention
from services.prompt_loader import get_prompt

class MessageHandler:
    def __init__(
        self,
        bot: Bot,
        reactions: ReactionHandler,
        openai_client: OpenAIClient,
        config_service: ConfigService
    ):
        self.bot = bot
        self.reactions = reactions
        self.openai_client = openai_client
        self.config_service = config_service

    async def handle_reactions(self, message):
        """メッセージに対して適切なリアクションを付ける"""
        if not self._should_add_reaction(message):
            return

        if message.author.bot:
            if random_true_with_probability(self.config_service.get_reaction_rate()):
                print("Botにはランダムでリアクションを付ける")
                return
            
        await self.reactions.fetchReaction(message_id=message.id, message_content=message.content)
        reactions = self.reactions.getReactions(message.id)

        for reaction in reactions:
            if random_true_with_probability(self.config_service.get_reaction_rate()):
                try:
                    await message.add_reaction(reaction)
                except Exception as e:
                    print(f"Error = {e}: リアクションが送れませんでした")

    async def handle_auto_response(self, message):
        """メンションが無い場合に自動で返信する"""
        if not self._should_auto_respond(message.channel.id, message.author.bot):
            return

        response = await self._generate_response(message, user_message=message.content)
        await message.channel.send(response)

    async def handle_mentions(self, message, client):
        """メンションがあった場合にキャラが返信をする"""
        if not (client.user.mentioned_in(message) or check_role_mention(message=message, client=client)):
            return

        user_message = self._clean_mentions(message.content)
        if user_message:
            response = await self._generate_response(message, user_message)
            await message.channel.send(response)

    def _should_add_reaction(self, message) -> bool:
        """リアクションを付けるかどうかをチェックする"""
        # メッセージが空でない
        # timesチャンネルでない
        # DEVチャンネルでない
        return (
            message.content.strip() and
            "times" not in message.channel.name and
            message.channel.id != self.config_service.get_channel_id("DEV")
        )

    def _clean_mentions(self, content: str) -> str:
        """メンション部分を削除する"""
        return re.sub(r'<@!?(\d+)>|<@!?(\w+)>|<@&(\d+)>', '', content).strip()

    async def _generate_response(self, message: str, user_message: str) -> str:
        """返信を生成する"""
        prompt = self._get_prompt(message.channel.id)
        return self.openai_client.get_response(
            prompt=prompt,
            user_message=user_message,
        )
    
    def _get_prompt(self, channel_id: int) -> str:
        """プロンプトを取得する"""
        pre_prompt = ""
        if channel_id == self.config_service.get_channel_id("FREE_TALK"):
            pre_prompt = "あなたが興味関心のある話題をテーマに雑談してください。"
        elif channel_id == self.config_service.get_channel_id("FB"):
            pre_prompt = "フィードバックをしてください。また、"
        elif channel_id == self.config_service.get_channel_id("PRAISE"):
            pre_prompt = "全力で褒めてください。また、"

        mbti_prompt = get_prompt(f"prompt/mbti/{self.bot.mbti_file_name}.txt")
        return f"{pre_prompt}{mbti_prompt}"
    
    def _is_auto_response_channel(self, channel_id: int) -> bool:
        free_talk_id = self.config_service.get_channel_id("FREE_TALK")
        fb_id = self.config_service.get_channel_id("FB")
        praise_id = self.config_service.get_channel_id("PRAISE")
        
        return channel_id in [free_talk_id, fb_id, praise_id]
    
    def _should_auto_respond(self, channel_id: int, is_bot: bool) -> bool:
        """自動返信するかどうかをチェックする"""
        is_free_talk = channel_id == self.config_service.get_channel_id("FREE_TALK")
        is_fb = channel_id == self.config_service.get_channel_id("FB")
        is_praise = channel_id == self.config_service.get_channel_id("PRAISE")

        if not is_free_talk and not is_fb and not is_praise:
            print("「フリートーク、FB、ほめる」以外は自動返信をしない")
            return False
            
        if is_bot and is_fb:
            print("Botに対してFBはしない")
            return False
        
        if is_bot and is_praise:
            print("Botに対して褒めない")
            return False
        
        # 確率で返信させる
        if is_free_talk and not random_true_with_probability(self.config_service.get_auto_reply_in_free_talk_rate()):
            print("フリートークは高確率で返信しない")
            return False
        if is_fb and not random_true_with_probability(self.config_service.get_auto_reply_rate()):
            print("FBは低確率で返信しない")
            return False
        if is_praise and not random_true_with_probability(self.config_service.get_auto_reply_rate()):
            print("ほめるは低確率で返信しない")
            return False

        return True