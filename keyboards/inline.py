from datetime import datetime
from enum import Enum, auto, IntEnum

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MainMenuAction(Enum):
    about = 'about'
    apointment = 'apointment'
    profile = 'profile'
    promo = 'promo'
    admin = 'admin'
    main_menu = 'main_menu'
    contacts = 'contacts'


class AdminMenu(CallbackData, prefix='a_menu'):
    level: int | None = None
    menu_name: str


class MainMenuCbData1(CallbackData, prefix="menu"):
    level: int | None = None
    menu_name: str
    page: int = 1
    promo_id: int | None = None
    doctor_id: int | None = None
    user_id: int | None = None
    fio_doctor: str | None = None
    date: str | None = None
    specialty_id: int | None = None
    per_page: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Клиника Пасман ℹ️": "about",
        "Запись к врачу 👩": "apointment",
        "Профиль 👤": "profile",
        "Акции 🎁": "promo",
    }
    for text, menu_name in btns.items():
        if menu_name == 'about':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=1, menu_name=menu_name))
        elif menu_name == 'promo':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=3, menu_name=menu_name))
        elif menu_name == 'apointment':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=4, menu_name=menu_name))
        elif menu_name == 'profile':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=6, menu_name=menu_name))

    return keyboard.adjust(*sizes).as_markup()


def get_user_main_admin_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Клиника Пасман ℹ️": "about",
        "Запись к врачу 👩": "apointment",
        "Профиль 👤": "profile",
        "Акции 🎁": "promo",
        "Админ": "admin"
    }
    for text, menu_name in btns.items():
        if menu_name == 'about':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=1, menu_name=menu_name))
        elif menu_name == 'promo':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=3, menu_name=menu_name))
        elif menu_name == 'apointment':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=4, menu_name=menu_name))
        elif menu_name == 'profile':
            keyboard.button(text=text, callback_data=MainMenuCbData1(level=6, menu_name=menu_name))
        elif menu_name == 'admin':
            keyboard.button(text=text, callback_data=AdminMenu(level=0, menu_name=menu_name))

    return keyboard.adjust(*sizes).as_markup()


def get_user_about_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Контакты", callback_data=MainMenuCbData1(level=2, menu_name='contact'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=level - 1, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_user_contacts_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=level - 1, menu_name='about'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_profile_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='История приемов', callback_data=MainMenuCbData1(level=7, menu_name='reception_history'))
    keyboard.button(text='История анализов ', callback_data=MainMenuCbData1(level=10, menu_name='analysis_menu'))
    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_doctors_btns(
        *,
        level: int,
        page: int,
        doctor_id: int,
        pagination_btns: dict,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    keyboard.button(text='Выбрать врача', callback_data=MainMenuCbData1(level=5, menu_name='calendar',
                                                                        doctor_id=doctor_id))
    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def get_promos_btns(
        *,
        level: int,
        page: int,
        promo_id: int,
        pagination_btns: dict,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def find_id(name, list2):
    for item in list2:
        if name in item:
            return item[name]


def get_receptions_history_doctor(
        *,
        level: int,
        page: int,
        pagination_btns: dict,
        data_for_button: list,
        page_button_list: list,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    new_data = []
    for name in page_button_list:
        id_ = find_id(name, data_for_button)
        new_data.append({'text': name, 'id': id_})
    for button_info in new_data:
        keyboard.button(text=button_info['text'], callback_data=MainMenuCbData1(level=8, menu_name='visit_dates',
                                                                                doctor_id=button_info['id']))

    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def get_receptions_history_date(
        *,
        level: int,
        page: int,
        pagination_btns: dict,
        page_button_list: list,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()
    for date_datetime in page_button_list:
        date_string = date_datetime[0].strftime("%d:%m:%Y")
        date_string_callback = date_datetime[0].strftime("%d-%m-%Y")
        keyboard.button(text=date_string,
                        callback_data=MainMenuCbData1(level=9, menu_name='diagnosis', date=date_string_callback))

    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=7, menu_name='reception_history'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def get_analysis_menu_btns(
        *,
        level: int,
        page: int,
        pagination_btns: dict,
        data_for_button: list,
        page_button_list: list,
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    new_data = []
    for name in page_button_list:
        id_ = find_id(name, data_for_button)
        new_data.append({'text': name, 'id': id_})
    for button_info in new_data:
        keyboard.button(text=button_info['text'], callback_data=MainMenuCbData1(level=11, menu_name='result_analysis',
                                                                                specialty_id=button_info['id'],
                                                                                per_page=page))

    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MainMenuCbData1(
                                                level=level,
                                                menu_name=menu_name,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_return_main_btns(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_return_date_btns(*, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=8, menu_name='visit_dates'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_web_btns(file: str, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Просмотреть результаты анализа', web_app=WebAppInfo(url=file))
    keyboard.button(text='Получить файл с результатом анализа', callback_data='send_file')
    keyboard.button(text='Назад', callback_data=MainMenuCbData1(level=10, menu_name='analysis_menu'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_admin_menu_btns(*, level: int, sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Рассылка", callback_data=AdminMenu(menu_name='mailling'))
    keyboard.button(text="Аналитика", callback_data=AdminMenu(menu_name='analytics'))
    keyboard.button(text="Редактировать акции", callback_data=AdminMenu(menu_name='edit_promo_menu'))
    keyboard.button(text="Редактировать приветственное сообщение", callback_data=AdminMenu(menu_name='replace_text_hi'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_edit_promo_btns(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Добавить Акцию", callback_data='add_promo')
    keyboard.button(text="Удалить Акцию", callback_data='delete_promo')
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_add_promo_btns(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Назад", callback_data=AdminMenu(menu_name='edit_promo_menu'))
    keyboard.button(text='Главное меню', callback_data=MainMenuCbData1(level=0, menu_name='main'))
    return keyboard.adjust(*sizes).as_markup()


def get_is_need_url_btns(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='yes'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='no'))

    return keyboard.adjust(*sizes).as_markup()


async def get_confirm_cancel(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Да', callback_data='yes')
    keyboard.button(text='Нет', callback_data='no')
    keyboard.button(text='Отмена', callback_data=AdminMenu(level=0, menu_name='admin'))

    return keyboard.adjust(*sizes).as_markup()


def get_cancel_btns(sizes: tuple[int, ...] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Отмена', callback_data=AdminMenu(level=0, menu_name='admin'))

    return keyboard.adjust(*sizes).as_markup()
