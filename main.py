import asyncio
from bot_manager import start_bot
from bot import all_bots
from reactions import Reactions

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    reactions = Reactions()

    for bot in all_bots:
        loop.create_task(start_bot(bot=bot, reactions=reactions))
    
    loop.run_forever()

    loop.close()
