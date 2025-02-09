import asyncio
from bot_manager import start_bot
from bot import allBots

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    for bot in allBots:
        loop.create_task(start_bot(bot=bot))
    
    loop.run_forever()

    loop.close()

