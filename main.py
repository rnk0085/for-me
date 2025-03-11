import asyncio
from src.services.reaction_handler import ReactionHandler
from src.services.discord_bot_manager import start_bot
from src.services.tasukuma_bot_manager import run_tasukuma
from src.models.bot import all_bots
from src.services.config_service import ConfigService

async def main():
    reactions = ReactionHandler(ConfigService())

    # MBTIボットとTaskumaボットの両方を起動
    tasks = [
        *[start_bot(bot=bot, reactions=reactions) for bot in all_bots],
        run_tasukuma()
    ]
    
    # すべてのBotが終了するまで待機
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

