from aiogram import types


async def get_contact_keyboard():
    kb_obj = [
        [
            types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb_obj, resize_keyboard=True, one_time_keyboard=True)
    return keyboard
