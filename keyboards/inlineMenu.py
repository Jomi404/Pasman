from enum import Enum, auto

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MainMenuAction(Enum):
    about = 'about'
    apointment = 'apointment'
    profile = 'profile'
    promo = 'promo'
    admin = 'admin'
    main_menu = 'main_menu'
    contacts = 'contacts'


class MainMenuCbData(CallbackData, prefix="menu"):
    action: MainMenuAction


def build_clinic_kb(sizes: tuple[int, ...] = (2,)) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Клиника Пасман ℹ️", callback_data=MainMenuCbData(action=MainMenuAction.about).pack(), )
    builder.button(text="Запись к врачу 👩‍⚕", callback_data=MainMenuCbData(action=MainMenuAction.apointment).pack(), )
    builder.button(text="Профиль 👤", callback_data=MainMenuCbData(action=MainMenuAction.profile).pack(), )
    builder.button(text="Акции 🎁", callback_data=MainMenuCbData(action=MainMenuAction.promo).pack(), )
    return builder.adjust(*sizes).as_markup()


def to_main_page_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="В главное меню", callback_data=MainMenuCbData(action=MainMenuAction.main_menu).pack(), )
    builder.adjust()
    return builder.as_markup()


def about_page_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Контакты", callback_data=MainMenuCbData(action=MainMenuAction.contacts).pack(), )
    builder.button(text="В главное меню", callback_data=MainMenuCbData(action=MainMenuAction.main_menu).pack(), )
    builder.adjust(1)
    return builder.as_markup()
