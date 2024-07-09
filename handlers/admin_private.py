import asyncio

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

import aiogram.filters as filters

from models.orm_query import update_text_hi
import utils
from filters import ChatTypeFilterMes, ChatTypeFilterCall, isAdmin
from keyboards import MainMenuCbData1, getKeyboardConfirm
from states import Admin
from handlers.menu_processing import get_menu_adm_content
from keyboards.inline import AdminMenu, get_return_main_btns, get_edit_promo_btns, get_add_promo_btns, \
    get_is_need_url_btns, get_confirm_cancel, get_cancel_btns

import models
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data.static import button_counters

admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilterMes(['private']))
admin_private_router.callback_query.filter(ChatTypeFilterCall(['private']))


@admin_private_router.callback_query(isAdmin(), AdminMenu.filter())
async def admin_menu(callback_query: CallbackQuery, callback_data: AdminMenu, session: AsyncSession, state: FSMContext):
    await callback_query.answer()
    print(button_counters)
    if callback_data.menu_name == 'admin':
        await state.set_state(Admin.menu)
        await state.set_data({})

    if callback_data.menu_name == 'replace_text_hi':
        await state.set_state(Admin.replace_txt_hi)
        await state.set_data({'message_id': callback_query.message.message_id})
        text = (f'Вы начали редактирование приветственного сообщения.\n\n'
                f'<b>Пожалуйста введите текст приветственного сообщения:</b>\n\n'
                f'<b>Шаг 1 из 1</b>')
        await callback_query.message.edit_caption(inline_message_id=callback_query.inline_message_id, caption=text,
                                                  parse_mode=ParseMode.HTML)
    elif callback_data.menu_name == 'edit_promo_menu':
        await state.set_state(Admin.edit_promo_menu)
        await state.set_data({})
        reply_markup = get_edit_promo_btns()
        await callback_query.message.edit_caption(inline_message_id=callback_query.inline_message_id,
                                                  caption='Выберите необходимое вам действие:',
                                                  reply_markup=reply_markup)
    elif callback_data.menu_name == 'mailling':
        await state.set_state(Admin.create_mailling)
        await state.set_data({})
        await state.set_data({'message_id': callback_query.message.message_id})
        text = (f'Вы начали создание рассылки.\n\n'
                f'<b>Пожалуйста введите название рассылки:</b>\n\n'
                f'<b>Шаг 1 из 3</b>')
        reply_markup = get_cancel_btns()
        await callback_query.message.edit_caption(inline_message_id=callback_query.inline_message_id, caption=text,
                                                  parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    elif callback_data.menu_name == 'analytics':
        text = (f'<b>about:</b> {button_counters["menu:1:about:1:::::::"]} clicks\n'
                f'<b>apointment:</b> {button_counters["menu:4:apointment:1:::::::"]} clicks\n'
                f'<b>profile:</b> {button_counters["menu:6:profile:1:::::::"]} clicks\n'
                f'<b>promo:</b> {button_counters["menu:3:promo:1:::::::"]} clicks\n'
                f'<b>contact:</b> {button_counters["menu:2:contact:1:::::::"]} clicks\n')
        reply_markup = get_return_main_btns()
        await callback_query.message.edit_caption(inline_message_id=callback_query.inline_message_id, caption=text,
                                                  parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    else:
        media, reply_markup = await get_menu_adm_content(
            session=session,
            level=callback_data.level,
            menu_name=callback_data.menu_name
        )
        photo = FSInputFile(media.media)
        my_media = types.input_media_photo.InputMediaPhoto(media=photo, caption=media.caption,
                                                           parse_mode=ParseMode.HTML)
        await callback_query.message.edit_media(media=my_media, reply_markup=reply_markup)


@admin_private_router.message(filters.StateFilter(Admin.replace_txt_hi))
async def process_confirm_text_hi(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({'text': message.text})
    await state.set_state(Admin.confirm_replace_txt_hi)
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте правильность приветственного сообщения.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 1 из 1</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_replace_txt_hi), F.data.startswith("no"))
async def process_confirm_no_txtHi(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.replace_txt_hi)
    caption = (f'Пожалуйста введите текст приветственного сообщения снова:\n\n'
               f'<b>Шаг 1 из 1</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_replace_txt_hi), F.data.startswith("yes"))
async def process_confirm_yes_txtHi(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    reply_markup = get_return_main_btns()
    # запрос к БД на вставку
    await models.update_text_hi(session=session, new_text=data['text'])
    await state.clear()
    caption = f'<b>Приветственное сообщения обновлено в БД.</b>'
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.callback_query(filters.StateFilter(Admin.edit_promo_menu), F.data.startswith('add_promo'))
async def select_btn_add_promo(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    await state.set_state(Admin.set_promo_name)
    await state.update_data({'message_id': callback_query.message.message_id})
    print(f'message_id {callback_query.message.message_id}')
    reply_markup = get_add_promo_btns()
    caption = (f'Пожалуйста введите <b>название акции</b>:\n\n'
               f'<b>Шаг 1 из 3</b>')
    await callback_query.message.edit_caption(inline_message_id=callback_query.inline_message_id, caption=caption,
                                              parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.message(filters.StateFilter(Admin.set_promo_name))
async def process_confirm_txtPromo(message: Message, state: FSMContext):
    await state.set_state(Admin.confirm_promo_name)
    data = await state.get_data()
    await state.update_data({'promo_name': message.text})
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте введенное название для акции.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 1 из 3</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_promo_name), F.data.startswith("no"))
async def process_confirm_no_txtPromo(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.set_promo_name)
    caption = (f'Пожалуйста введите <b>название акции</b> снова:\n\n'
               f'<b>Шаг 1 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_promo_name), F.data.startswith("yes"))
async def process_confirm_yes_txtHi(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.set_promo_desc)
    caption = (f'Пожалуйста введите <b>Описание акции</b>:\n\n'
               f'<b>Шаг 2 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.message(filters.StateFilter(Admin.set_promo_desc))
async def process_confirm_descPromo(message: Message, state: FSMContext):
    await state.set_state(Admin.confirm_promo_desc)
    data = await state.get_data()
    await state.update_data({'promo_description': message.text})
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте введенное описание акции.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 2 из 3</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_promo_desc), F.data.startswith("no"))
async def process_confirm_no_descPromo(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.set_promo_desc)
    caption = (f'Пожалуйста введите <b>описание акции</b> снова:\n\n'
               f'<b>Шаг 2 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_promo_desc), F.data.startswith("yes"))
async def process_confirm_yes_descPromo(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.set_state(Admin.is_need_url)
    reply_markup = get_is_need_url_btns()
    print(data)
    caption = (f'Нужно ли добавить ссылку на акцию?\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.callback_query(filters.StateFilter(Admin.is_need_url), F.data.startswith("no"))
async def process_confirm_no_need_url(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    new_promo = {'promo_name': data['promo_name'],
                 'promo_description': data['promo_description'],
                 'promo_url': ''}
    # делаем вставку данных
    await models.orm_add_promo(session=session, promo=new_promo)
    await state.clear()
    reply_markup = get_add_promo_btns()
    caption = f'<b>Акция успешно добавлена в БД.</b>'
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.callback_query(filters.StateFilter(Admin.is_need_url), F.data.startswith("yes"))
async def process_send_url(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.send_url)
    caption = (f'Пожалуйста отправьте ссылку на Акцию:\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.message(filters.StateFilter(Admin.send_url))
async def process_confirm_urlPromo(message: Message, state: FSMContext):
    await state.set_state(Admin.confirm_promo_send_url)
    data = await state.get_data()
    await state.update_data({'promo_url': message.text})
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте отправленную ссылку на акцию.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 3 из 3</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_promo_send_url), F.data.startswith("no"))
async def process_confirm_no_urlPromo(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.send_url)
    caption = (f'Пожалуйста отправьте <b>ссылку на акцию</b> снова:\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_promo_send_url), F.data.startswith("yes"))
async def process_confirm_yes_urlPromo(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    new_promo = {'promo_name': data['promo_name'],
                 'promo_description': data['promo_description'],
                 'promo_url': data['promo_url']}
    # делаем вставку данных
    await models.orm_add_promo(session=session, promo=new_promo)
    await state.clear()
    reply_markup = get_add_promo_btns()
    caption = f'<b>Акция успешно добавлена в БД.</b>'
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.callback_query(filters.StateFilter(Admin.edit_promo_menu), F.data == 'delete_promo')
async def process_delete_promo(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state(Admin.get_promo_name)
    await state.update_data({'message_id': callback_query.message.message_id})
    caption = f'Пожалуйста введите <b>название акции</b> <b>которую хотите удалить</b>:\n\n'
    await callback_query.message.edit_caption(inline_message_id=callback_query.inline_message_id, caption=caption,
                                              parse_mode=ParseMode.HTML)


@admin_private_router.message(filters.StateFilter(Admin.get_promo_name))
async def process_confirm_delPromo(message: Message, state: FSMContext):
    await state.set_state(Admin.get_confirm_name_del)
    data = await state.get_data()
    await state.update_data({'promo_name': message.text})
    reply_markup = await get_confirm_cancel()
    caption = f'Вы уверены что хотите удалить эту <b>{message.text}</b> акцию.'
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.get_confirm_name_del), F.data.startswith("no"))
async def process_confirm_no_delPromo(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.get_promo_name)
    caption = 'Пожалуйста введите <b>название акции</b> снова:'
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.get_confirm_name_del), F.data.startswith("yes"))
async def process_confirm_yes_delPromo(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    promo_name = data['promo_name']
    await models.orm_delete_promo(session=session, promo_name=promo_name)
    await state.clear()
    caption = 'Акция успешно удалена.'
    reply_markup = get_return_main_btns()
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.message(filters.StateFilter(Admin.create_mailling))
async def process_confirm_mailling(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({'mailling_name': message.text})
    await state.set_state(Admin.confirm_mailling_name)
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте название рассылки.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 1 из 3</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_mailling_name), F.data.startswith("no"))
async def process_confirm_no_mailling(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.create_mailling)
    caption = (f'Пожалуйста введите название рассылки снова:\n\n'
               f'<b>Шаг 1 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_mailling_name), F.data.startswith("yes"))
async def process_confirm_yes_mailling(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.input_mailling_desc)
    caption = (f'Пожалуйста введите <b>Описание рассылки</b>:\n\n'
               f'<b>Шаг 2 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.message(filters.StateFilter(Admin.input_mailling_desc))
async def process_confirm_descMailling(message: Message, state: FSMContext):
    await state.set_state(Admin.confirm_mailling_desc)
    data = await state.get_data()
    await state.update_data({'mailling_description': message.text})
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте введенное описание рассылки.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 2 из 4</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_mailling_desc), F.data.startswith("no"))
async def process_confirm_no_descMailling(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.input_mailling_desc)
    caption = (f'Пожалуйста введите <b>описание рассылки</b> снова:\n\n'
               f'<b>Шаг 2 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_mailling_desc), F.data.startswith("yes"))
async def process_confirm_yes_descMailling(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await state.set_state(Admin.is_need_btn)
    reply_markup = get_is_need_url_btns()
    print(data)
    caption = (f'Нужно ли добавить кнопку к рассылке?\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.callback_query(filters.StateFilter(Admin.is_need_btn), F.data.startswith("no"))
async def process_sending_mailing(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    users = await models.orm_get_users(session)
    for user in users:
        await utils.bot.send_message(chat_id=user, text=f"{data['mailling_name']}\n{data['mailling_description']}")
    caption = 'Рассылка отправлена.'
    reply_markup = get_return_main_btns()
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@admin_private_router.callback_query(filters.StateFilter(Admin.is_need_btn), F.data.startswith("yes"))
async def process_input_text_btn(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.input_text_btn)
    caption = (f'Пожалуйста отправьте название кнопки для рассылки:\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.message(filters.StateFilter(Admin.input_text_btn))
async def process_confirm_input_text_btn(message: Message, state: FSMContext):
    await state.set_state(Admin.confirm_input_text_btn)
    data = await state.get_data()
    await state.update_data({'mailling_button': message.text})
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте отправленное название для кнопки рассылки.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 3 из 3</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_input_text_btn), F.data.startswith("no"))
async def process_confirm_no_input_text_btn(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.input_text_btn)
    caption = (f'Пожалуйста введите название рассылки снова:\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_input_text_btn), F.data.startswith("yes"))
async def process_confirm_yes_input_text_btn(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.input_url_btn)
    caption = (f'Пожалуйста отправьте <b>ссылку на акционное предложение</b>:\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.message(filters.StateFilter(Admin.input_url_btn))
async def process_confirm_input_url_btn(message: Message, state: FSMContext):
    await state.set_state(Admin.confirm_input_url_btn)
    data = await state.get_data()
    await state.update_data({'mailling_url': message.text})
    reply_markup = await getKeyboardConfirm()
    caption = (f'Вы отправили <b>{message.text}</b>\n\n'
               f'Пожалуйста проверьте отправленную ссылку на акцию.\n'
               f'И нажмите соответствующую клавишу <b>Верно/Неверно</b>\n\n'
               f'<b>Шаг 3 из 3</b>')
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await utils.bot.edit_message_caption(chat_id=message.from_user.id, message_id=data['message_id'], caption=caption,
                                         reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_input_url_btn), F.data.startswith("no"))
async def process_confirm_no_input_url_btn(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Admin.input_url_btn)
    caption = (f'Пожалуйста отправьте <b>ссылку на акцию</b> снова:\n\n'
               f'<b>Шаг 3 из 3</b>')
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML)


@admin_private_router.callback_query(filters.StateFilter(Admin.confirm_input_url_btn), F.data.startswith("yes"))
async def process_confirm_yes_input_url_btn(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    users = await models.orm_get_users(session)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text=data['mailling_button'],
        url=data['mailling_url'])
    )
    reply_markup_mailling = keyboard.as_markup()
    for user in users:
        await utils.bot.send_message(chat_id=user, text=f"{data['mailling_name']}\n{data['mailling_description']}", reply_markup=reply_markup_mailling)
    caption = 'Рассылка отправлена.'
    reply_markup = get_return_main_btns()
    await callback.message.edit_caption(inline_message_id=callback.inline_message_id, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=reply_markup)



@admin_private_router.message()
async def input_chat(message: Message):
    await message.reply(text="Я вас, к сожалению, не понимаю. 👾\n"
                             "Попробуйте воспользоваться /menu ✅\n"
                             "Чтобы обновить бота, нажмите /start 🤖")
    await asyncio.sleep(3)
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id + 1)
    await utils.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
