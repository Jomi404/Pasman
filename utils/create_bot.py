from aiogram import Bot
from config_data.configuration import Config
from config_data import load_config
config: Config = load_config()
bot = Bot(token=config.tg_bot.token)
