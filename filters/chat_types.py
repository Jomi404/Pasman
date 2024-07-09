from aiogram.filters import Filter
from aiogram import Bot, types


class ChatTypeFilterMes(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class ChatTypeFilterCall(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, callback: types.CallbackQuery) -> bool:
        return callback.message.chat.type in self.chat_types
