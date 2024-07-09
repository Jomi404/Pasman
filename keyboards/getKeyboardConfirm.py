from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


async def getKeyboardConfirm():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Верно', callback_data='yes'))
    keyboard.add(types.InlineKeyboardButton(text='Неверно', callback_data='no'))
    keyboard.adjust(2)

    return keyboard.as_markup()
