from aiogram import types
from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from models import orm_query


class isPatient(Filter):

    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        return await orm_query.isPatient(session=session, user_id=message.from_user.id)
