import asyncio
import logging
from aiogram import types


from engine import create_db
from middlewares.db_middlewares import DataBaseSession
from engine import session_marker
import utils


async def main(dp: utils.create_dp.Dispatcher):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s'
                                                   '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')
    await create_db()
    dp.update.middleware(DataBaseSession(session_pool=session_marker))
    # Пропускаем накопившиеся апдейты и запускаем polling
    await utils.bot.delete_webhook(drop_pending_updates=True)
    await utils.bot.set_my_commands(commands=utils.private, scope=types.BotCommandScopeAllPrivateChats())
    try:
        await dp.start_polling(utils.bot)
    finally:
        await utils.bot.session.close()


if __name__ == "__main__":
    asyncio.run(main(utils.dp))
