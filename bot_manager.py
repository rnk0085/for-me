import discord
from services.bot import Bot
from services.message_handler import MessageHandler
from services.periodic_message_service import PeriodicMessageService
from services.reaction_handler import ReactionHandler
from services.openai_client import OpenAIClient
from services.config_service import ConfigService
from services.discord_client_setup import setup_discord_client
from discord.ext import tasks

class BotManager:
    def __init__(
        self,
        bot: Bot,
        discord_client: discord.Client,
        message_handler: MessageHandler,
        periodic_message_service: PeriodicMessageService,
    ):
        self.bot = bot
        self.client = discord_client
        self.message_handler = message_handler
        self.periodic_message_service = periodic_message_service
        self.token = ConfigService().get_discord_token(bot.mbti_type)

    def setup_events(self):
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')
            self.periodic_message.start()

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            
            await self.message_handler.handle_reactions(message)
            await self.message_handler.handle_auto_response(message)
            await self.message_handler.handle_mentions(message, self.client)

    @tasks.loop(minutes=1)
    async def periodic_message(self):
        await self.periodic_message_service.send_random_message(self.client)

    async def start(self):
        self.setup_events()
        await self.client.start(self.token)

async def start_bot(bot: Bot, reactions: ReactionHandler):
    bot_manager = BotManager(
        bot=bot,
        discord_client=setup_discord_client(),
        message_handler=MessageHandler(bot, reactions, OpenAIClient(ConfigService()), ConfigService()),
        periodic_message_service=PeriodicMessageService(bot, OpenAIClient(ConfigService()), ConfigService()),
    )
    await bot_manager.start()