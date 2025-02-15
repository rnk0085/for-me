import asyncio
from bot_manager import start_bot
from services.bot import all_bots
from services.reaction_handler import ReactionHandler
from services.config_service import ConfigService

async def main():
    reactions = ReactionHandler(ConfigService())

    # すべてのBotを並列実行
    tasks = [start_bot(bot=bot, reactions=reactions) for bot in all_bots]
    
    # すべてのBotが終了するまで待機
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

