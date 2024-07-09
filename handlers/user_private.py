from datetime import datetime

import pdfkit
import requests
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery, URLInputFile, InputFile, \
    BufferedInputFile

from aiogram.types import FSInputFile
from aiogram3_calendar.calendar_types import SimpleCalendarCallback, SimpleCalendarAction
from sqlalchemy.ext.asyncio import AsyncSession

from handlers import menu_processing
from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
import aiogram.filters as filters
import logging
from filters import isPatient
from models.orm_query import orm_add_user, orm_get_user_info, orm_get_doctor_info, orm_add_request, get_analysis_file

import utils
from states import Form, Record, MenuState, Admin
import re
from keyboards import get_contact_keyboard
from keyboards import getKeyboardConfirm, get_return_main_btns
from logger import CustomFormatter
from filters import ChatTypeFilterMes, ChatTypeFilterCall
import models
from keyboards.inline import MainMenuCbData1

from handlers.menu_processing import get_menu_content
from data.static import button_counters

'######################################################################################################################'
from my_calendar import SimpleCalendar

'######################################################################################################################'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilterMes(['private']))
user_private_router.callback_query.filter(ChatTypeFilterCall(['private']))

'''
Отслеживание нажатий сделать через middleware
user_private_router.message.outer_middleware(CounterMiddlewareStartCmd())
user_private_router.message.outer_middleware(CounterMiddlewareMenuCmd())
'''

'######################################################################################################################'
"""Commands"""
'######################################################################################################################'


async def exists(session: AsyncSession, user_id: int):
    users = await models.orm_query.orm_get_users_start(session=session)
    return True if user_id in users else False


@user_private_router.message(CommandStart())
async def cmdStart(message: types.Message, session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    if await exists(session=session, user_id=user_id):
        dataUser = await models.getFormDataCrm(session, user_id)
        # Добавить сбор из БД
        string_bd = await models.orm_query.get_text_hi(session=session, text_id=1)
        formatted_string = string_bd.replace("{user_name}", dataUser.full_name)
        # функция форматирования с ключевыми словами
        await utils.bot.send_message(user_id, f"{formatted_string}"
                                              f"\n✅Весь функционал бота вам доступен.\n"
                                              f"Используйте /menu для взаимодействия с ботом.")
    else:
        await state.set_state(Form.full_name)

        await utils.bot.send_message(message.from_user.id, "Пожалуйста, введите ваше ФИО:")


@user_private_router.message(Command('help'))
async def cmdHelp(message: Message, state: FSMContext):
    await state.clear()
    await utils.bot.send_message(message.from_user.id, text='''Что умеет бот:

- Присылать результаты незамедлительно по окончании лабораторного исследования;

- Рисовать график изменения лабораторных показателей на основе полученных ранее результатов;

- Описывать результаты и рекомендовать подходящего специалиста для консультации.

Как пользоваться ботом:

- Бот может присылать и отображать результаты исследований всех пациентов, в электронной карте которых в базе данных ЦНМТ указан ваш номер телефона. Если добавить пациента не получилось, обратитесь к администратору в любом нашем филиале с удостоверением личности для проверки информации в базе данных.

- Текущие результаты исследования на официальном бланке бот присылает автоматически в любом состоянии меню, даже если у пользователя в данный момент выбран другой пациент. Для доступа ко всем ранее полученным бланкам результатов нажмите на имя бота вверху экрана и выберите вкладку «файлы».

- После получения текущего результата на бланке бот предложит ознакомиться с интерпретацией исследованных показателей. Для интерпретации ранее полученных результатов и оценки динамики изменения показателей в виде графиков, нажмите кнопку меню, а затем выберете пункт «Вернуться к архиву результатов». Далее с помощью кнопочного меню вы можете выбрать один из наиболее 100 популярных показателей или воспользуйтесь поиском.

Запись к врачу по телефону: +79999999999

Поддержка @test. Но если у вас что-то сломалось, попробуйте /start перед обращением.''')


@user_private_router.message(isPatient(), Command("menu"))
async def cmdMenu(message: Message, session: AsyncSession, state: FSMContext):
    await state.set_state(None)
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main', user_id=message.from_user.id)
    print(media.media)
    photo = FSInputFile(media.media)
    await utils.bot.send_photo(message.from_user.id, photo=photo, caption=media.caption, reply_markup=reply_markup)


@user_private_router.callback_query(MainMenuCbData1.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MainMenuCbData1, session: AsyncSession,
                    state: FSMContext):
    await callback.answer()
    try:
        button_counters[callback.data] += 1
    except:
        pass
    if callback_data.menu_name == 'main':
        await state.set_state(MenuState.main)
        await state.clear()
    elif callback_data.menu_name == 'profile':
        await state.set_state(MenuState.profile)
    elif callback_data.menu_name == 'contact':
        await state.set_state(MenuState.contact)
    elif callback_data.menu_name == 'about':
        await state.set_state(MenuState.about)
    elif callback_data.menu_name == 'reception_history':
        await state.set_state(MenuState.reception_history)
    elif callback_data.menu_name == 'visit_dates':
        await state.set_state(MenuState.visit_dates)
    elif callback_data.menu_name == 'result_analysis':
        await state.set_state(Record.select_date)
        await state.set_state(MenuState.result_analysis)
        await state.set_data({'specialty_id': callback_data.specialty_id})
        await state.update_data({'user_id': callback.from_user.id})

    if callback_data.menu_name == 'calendar':
        await state.set_state(Record.select_date)
        message_id = callback.message.message_id
        await state.set_data({'doctor_id': callback_data.doctor_id})
        await state.update_data({'message_id': message_id})

    media, reply_markup = await get_menu_content(
        session=session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        page=callback_data.page,
        doctor_id=callback_data.doctor_id,
        user_id=callback.from_user.id,
        state=state,
        date=callback_data.date,
        specialty_id=callback_data.specialty_id,
        per_page=callback_data.per_page,

    )
    photo = FSInputFile(media.media)
    my_media = types.input_media_photo.InputMediaPhoto(media=photo, caption=media.caption,
                                                       parse_mode=ParseMode.HTML)
    await callback.message.edit_media(media=my_media, reply_markup=reply_markup)


def validateFio(fio: str) -> bool:
    pattern = re.compile(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$')
    return bool(pattern.match(fio))


@user_private_router.message(~isPatient(), Command("menu"))
async def no_patient(message: Message):
    await utils.bot.send_message(message.from_user.id, text="⛔ Чтобы получить доступ к меню\n"
                                                            "вам необходимо авторизироваться, введите /start")


'######################################################################################################################'


def create_markdown_link(text, url):
    return f"[{text}]({url})"


@user_private_router.callback_query(F.data == 'send_file')
async def send_file(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback_query.answer()
    data = await state.get_data()
    file_result = await get_analysis_file(session=session, user_id=data['user_id'], specialty_id=data['specialty_id'])
    pdf_file = URLInputFile(url=file_result)
    await utils.bot.send_document(callback_query.from_user.id, document=pdf_file)


@user_private_router.callback_query(SimpleCalendarCallback.filter(), filters.StateFilter(Record.select_date))
async def process_selected_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext,
                                session: AsyncSession):
    current_state = await state.get_state()
    print(f"Текущие состояние: {current_state}")
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        keyboard = get_return_main_btns()
        selected_date = date.strftime("%d:%m:%Y")
        await state.update_data({'selected_date': str(selected_date)})
        data = await state.get_data()
        photo = FSInputFile('W:\\Чист\\Monitoring\\data\\image\\calendar.jpg')
        my_media = types.input_media_photo.InputMediaPhoto(media=photo,
                                                           caption="Заявка успешно создана и передана менеджеру.\n"
                                                                   "Спасибо за обращение!",
                                                           parse_mode=ParseMode.HTML)
        await state.set_state(Record.send_request)
        await send_request(state=state, session=session, user_id=callback_query.from_user.id)
        await callback_query.message.edit_media(media=my_media, inline_message_id=str(data['message_id']),
                                                reply_markup=keyboard)


async def send_request(state: FSMContext, session: AsyncSession, user_id):
    current_state = await state.get_state()
    print(f"Текущие состояние: {current_state}")
    data = await state.get_data()
    doctor_info = await orm_get_doctor_info(session=session, doctor_id=data['doctor_id'])
    user_info = await orm_get_user_info(session=session, user_id=user_id)
    date = data['selected_date']
    date_datetime = datetime.strptime(date, "%d:%m:%Y")
    request_data = {'user_id': user_id,
                    'fio_client': user_info.full_name,
                    'age_client': user_info.age,
                    'select_direction': doctor_info.direction,
                    'fio_doctor': doctor_info.fio_doctor,
                    'date': date_datetime,
                    'phone_number': user_info.phone_number}

    await orm_add_request(session=session, request=request_data)

    text_request = (f'{user_info.full_name} {user_info.age} лет:\n'
                    f'Интересуемый врач {doctor_info.direction}\n'
                    f'{doctor_info.fio_doctor}\n'
                    f'Удобная дата приёма:\n'
                    f'{date}\n'
                    f'Телефон:\n'
                    f'{user_info.phone_number}')
    await utils.bot.send_message(chat_id=-4288255049, text=text_request)


@user_private_router.message(filters.StateFilter(Form.full_name))
async def proccesFullName(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    keyboard = await getKeyboardConfirm()
    current_state = await state.get_state()
    print(f"Текущие состояние: {current_state}")
    if validateFio(full_name):
        await utils.bot.send_message(message.from_user.id, f"Пожалуйста проверьте корректность введённых данных.\n"
                                                           f"Вы ввели: {message.text}", reply_markup=keyboard)
        await state.set_data({'full_name': full_name})
        await state.set_state(Form.confirmFio)
    else:
        await utils.bot.send_message(message.from_user.id, "Пожалуйста введите данные в формате Фамилия Имя Отчество:")


@user_private_router.message(filters.StateFilter(Form.phone), F.contact)
async def processPhone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    keyboard = await getKeyboardConfirm()
    if message.contact.user_id == message.from_user.id:
        await utils.bot.send_message(message.from_user.id, f"Пожалуйста проверьте корректность отправленных данных.\n"
                                                           f"Вы отправили: {phone}",
                                     reply_markup=keyboard)
        await state.update_data({'phone': phone})
        data = await state.get_data()
        await state.set_state(Form.confirmPhone)
        try:
            await utils.bot.delete_message(message.chat.id, data["message_id"])
            logger.info(f"Удаление сообщения {data['message_id']} ")
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")

    else:
        await utils.bot.send_message(message.from_user.id, "Пожалуйста нажмите кнопку Отправить номер телефона:")


@user_private_router.message(filters.StateFilter(Form.phone))
async def user_not_sent_phoneNum(message: types.Message):
    await utils.bot.send_message(message.from_user.id, "Вы ввели недопустимые данные.\n"
                                                       "Пожалуйста нажмите кнопку Отправить номер телефона.")


@user_private_router.message(filters.StateFilter(Form.age), F.text)
async def processAge(message: types.Message, state: FSMContext):
    age = message.text.strip()
    keyboard = await getKeyboardConfirm()
    if re.match(r'^\d+$', age) and 0 <= int(age) <= 120:
        await utils.bot.send_message(message.from_user.id, f"Пожалуйста проверьте корректность введёных данных.\n"
                                                           f"Вы ввели: {age}", reply_markup=keyboard)
        await state.update_data({'age': int(age)})
        await state.set_state(Form.confirmAge)
    else:
        await utils.bot.send_message(message.from_user.id, "Пожалуйста отправьте действительный возраст (0 - 130):")


'######################################################################################################################'
"""Callback_query"""
'######################################################################################################################'


@user_private_router.callback_query(filters.StateFilter(Form.confirmAge), F.data.startswith("yes"))
async def process_confirm_yes_Age(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer("Данные подтверждены.")
    await state.set_state(Form.finishReg)
    data = await state.get_data()
    await orm_add_user(session=session, user_id=callback.from_user.id, age=data['age'], full_name=data['full_name'],
                       phone_number=data["phone"])
    await models.orm_query.insert_user(session=session, user_id=callback.from_user.id)
    await utils.bot.send_message(callback.from_user.id, "Регистрация завершена.")
    await state.clear()


@user_private_router.callback_query(filters.StateFilter(Form.confirmAge), F.data.startswith("no"))
async def process_confirm_no_Age(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.age)
    await utils.bot.send_message(callback.from_user.id, "Пожалуйста, введите ваш возраст снова:")


@user_private_router.callback_query(filters.StateFilter(Form.confirmPhone), F.data.startswith("yes"))
async def process_confirm_yes_phone(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Данные подтверждены.")
    await state.set_state(Form.age)
    await utils.bot.send_message(callback.from_user.id, "Пожалуйста, введите ваш возраст:")


@user_private_router.callback_query(filters.StateFilter(Form.confirmPhone), F.data.startswith("no"))
async def process_confirm_yes_fio(callback: types.CallbackQuery, state: FSMContext):
    keyboard = await get_contact_keyboard()
    await state.set_state(Form.phone)
    sent_message = await utils.bot.send_message(callback.from_user.id,
                                                "Пожалуйста нажмите на кнопку Отправить номер телефона снова:",
                                                reply_markup=keyboard)
    message_id = sent_message.message_id
    await state.update_data({'message_id': message_id})


@user_private_router.callback_query(filters.StateFilter(Form.confirmFio), F.data.startswith("yes"))
async def process_confirm_yes_fio(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Данные подтверждены.")
    keyboard = await get_contact_keyboard()
    await state.set_state(Form.phone)
    sent_message = await utils.bot.send_message(callback.from_user.id,
                                                f"Пожалуйста нажмите кнопку Отправить номер телефона:",
                                                reply_markup=keyboard)
    message_id = sent_message.message_id
    await state.update_data({'message_id': message_id})


@user_private_router.callback_query(filters.StateFilter(Form.confirmFio), F.data.startswith("no"))
async def process_confirm_no_fio(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    print(f"Текущие состояние: {current_state}")
    await state.set_state(Form.full_name)
    await utils.bot.send_message(callback.from_user.id, "Пожалуйста, введите ваше ФИО снова:")
