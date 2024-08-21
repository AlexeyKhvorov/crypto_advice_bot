import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import commands
import handlers
import functions
from bot import bot


async def main():
    dp = Dispatcher()
    dp.include_router(handlers.router)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(functions.cleaning_files, trigger='interval', seconds=3600,
                      start_date=datetime.now())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=commands.commands, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')




