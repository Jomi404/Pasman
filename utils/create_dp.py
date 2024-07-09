from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import user_private_router, admin_private_router

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_routers(user_private_router, admin_private_router)
