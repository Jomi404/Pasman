from datetime import datetime

import models
from models.orm_query import orm_get_user_info, orm_get_reception_history_date_info, get_dates_by_user_id, \
    get_dig_by_user_id, get_analysis_file, get_name_specialty_by_id
from my_calendar import SimpleCalendar
from aiogram.types import InputMediaPhoto
from keyboards.inline import get_user_main_btns, get_user_about_btns, get_user_contacts_btns, get_promos_btns, \
    get_doctors_btns, get_profile_btns, get_receptions_history_doctor, get_return_main_btns, \
    get_receptions_history_date, get_return_date_btns, get_analysis_menu_btns, get_web_btns, get_user_main_admin_btns, \
    get_admin_menu_btns
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

import utils

from paginator import Paginator
from states import Admin


async def main_menu(session, level, menu_name, user_id):
    banner = await models.orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    isAdmin = await models.orm_query.isAdmins(session=session, user_id=user_id)
    print(isAdmin)
    if isAdmin:
        kbds = get_user_main_admin_btns(level=level, sizes=(1, 1, 2, 1))
    else:
        kbds = get_user_main_btns(level=level, sizes=(1, 1, 2))

    return image, kbds


async def about_menu(session, level, menu_name):
    banner = await models.orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_about_btns(level=level, sizes=(1, 2))

    return image, kbds


async def contacts_menu(session, level, menu_name):
    banner = await models.orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_contacts_btns(level=level, sizes=(1, 2))

    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def promos_menu(session, level, menu_name, page):
    banner = await models.orm_get_banner(session, 'promo')
    promos = await models.orm_get_promos(session)

    paginator = Paginator(promos, page=page)
    promo = paginator.get_page()[0]

    if promo.promo_url == '' or promo.promo_url is None:
        caption = (f'<strong>{promo.promo_name}</strong>\n\n'
                   f'{promo.promo_description}\n'
                   f"<strong>Акция {paginator.page} из {paginator.pages}</strong>")
    else:
        url_more = utils.getHyperLink(url=promo.promo_url, title=promo.promo_name)
        caption = (f'<strong>{promo.promo_name}</strong>\n\n'
                   f'{promo.promo_description}\n'
                   f"Подробнее можете узнать тут 👉 {url_more}\n"
                   f"<strong>Акция {paginator.page} из {paginator.pages}</strong>")

    image = InputMediaPhoto(media=banner.image, caption=caption)

    pagination_btns = pages(paginator)

    kbds = get_promos_btns(
        level=level,
        page=page,
        promo_id=promo.id,
        pagination_btns=pagination_btns,
    )
    return image, kbds


async def doctors_menu(session, level, menu_name, page):
    doctors = await models.orm_get_doctors(session=session)

    paginator = Paginator(doctors, page=page)
    doctor = paginator.get_page()[0]
    image_doctor = await models.orm_get_banner_doctor(session=session, doctor_id=doctor.doctor_id)

    image = InputMediaPhoto(
        media=image_doctor.image,
        caption=f"<strong>{doctor.fio_doctor}</strong>\n"
                f"Направление - {doctor.direction}\n"
                f"doctor_id - {doctor.doctor_id}\n"
                f"<strong>Врач {paginator.page} из {paginator.pages}</strong>"
    )

    pagination_btns = pages(paginator)

    kbds = get_doctors_btns(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        doctor_id=doctor.doctor_id,
    )

    return image, kbds


async def reception_history_menu(session, level, user_id, page, state: FSMContext):
    banner = await models.orm_get_banner(session, 'reception_history')
    # нужно получить фамилии врачей у кого был пользователь и их id
    doctors_fios_ids = await models.get_doctors_fio_id(session=session, user_id=user_id)
    data_for_button = [{fio_doctor: doctor_id} for fio_doctor, doctor_id in doctors_fios_ids]
    fio_doctors = [doctors_fios_ids[i][0] for i in range(len(doctors_fios_ids))]

    paginator = Paginator(fio_doctors, page=page, per_page=4)
    page_button_list = paginator.get_page()

    image = InputMediaPhoto(
        media=banner.image,
        caption='Выберите врача:'

    )

    pagination_btns = pages(paginator)

    kbds = get_receptions_history_doctor(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        page_button_list=page_button_list,
        data_for_button=data_for_button,
    )

    return image, kbds


async def visit_dates(session, level, user_id, page, state: FSMContext, doctor_id):
    banner = await models.orm_get_banner(session, 'visit_dates')
    await state.set_data({'doctor_id': doctor_id})
    dates = await get_dates_by_user_id(session=session, user_id=user_id, doctor_id=doctor_id)

    paginator = Paginator(dates, page=page, per_page=4)

    page_button_list = paginator.get_page()

    image = InputMediaPhoto(
        media=banner.image,
        caption='Выберите дату:'

    )

    pagination_btns = pages(paginator)

    kbds = get_receptions_history_date(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        page_button_list=page_button_list
    )

    return image, kbds


async def diagnosis_menu(session, level, user_id, state: FSMContext, date):
    banner = await models.orm_get_banner(session, 'diagnosis')
    data = await state.get_data()
    diagnosis = await get_dig_by_user_id(session, user_id=user_id, doctor_id=data['doctor_id'], date=date)
    image = InputMediaPhoto(
        media=banner.image,
        caption=f'Ваш диагноз: {diagnosis}'

    )

    kbds = get_return_main_btns()

    return image, kbds


async def calendar_menu(session, level, menu_name):
    banner = await models.orm_get_banner(session, menu_name)  # calendar
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = await SimpleCalendar().start_calendar()
    return image, kbds


async def profile_menu(session, level, menu_name, user_id):
    banner = await models.orm_get_banner(session, menu_name)
    user_info = await orm_get_user_info(session=session, user_id=user_id)
    caption = f'<b>{user_info.full_name}</b>\nВаш номер телефона: <b>{user_info.phone_number}</b>'
    image = InputMediaPhoto(media=banner.image, caption=caption)

    kbds = get_profile_btns(level=level, sizes=(1, 1, 2))

    return image, kbds


async def analysis_menu(session, level, page):
    banner = await models.orm_get_banner(session, 'analysis_menu')
    # нужно получить фамилии врачей у кого был пользователь и их id
    name_specialty_id = await models.get_name_specialty_id(session=session)
    data_for_button = [{name_specialty: specialty_id} for name_specialty, specialty_id in name_specialty_id]
    name_specialtys = [name_specialty_id[i][0] for i in range(len(name_specialty_id))]

    paginator = Paginator(name_specialtys, page=page, per_page=4)
    page_button_list = paginator.get_page()
    print(page)
    image = InputMediaPhoto(
        media=banner.image,
        caption='Выберите специальность врача:'

    )

    pagination_btns = pages(paginator)

    kbds = get_analysis_menu_btns(
        level=level,
        page=page,
        pagination_btns=pagination_btns,
        page_button_list=page_button_list,
        data_for_button=data_for_button,
    )

    return image, kbds


async def result_analysis_menu(session: AsyncSession, level: int, user_id: int, specialty_id: id, page: int,
                               state: FSMContext, per_page):
    banner = await models.orm_get_banner(session, 'result_analysis')
    print(per_page)
    file_result = await get_analysis_file(session=session, user_id=user_id, specialty_id=specialty_id)
    print(f'file_result: {file_result}')
    if file_result is None:
        image, kbds = await analysis_menu(session, level=10, page=per_page)
    else:
        name_specialty = await get_name_specialty_by_id(session=session, specialty_id=specialty_id)
        image = InputMediaPhoto(
            media=banner.image,
            caption=f'Результаты анализов категории {name_specialty}:'

        )

        kbds = get_web_btns(file_result, (1, 1, 2,))
    return image, kbds


async def get_menu_content(
        session: AsyncSession,
        menu_name: str,
        level: int | None = None,
        page: int | None = None,
        doctor_id: int | None = None,
        user_id: int | None = None,
        state: FSMContext | None = None,
        date: str | None = None,
        specialty_id: int | None = None,
        per_page: int | None = None
):
    if level == 0:
        return await main_menu(session, level, menu_name, user_id)
    elif level == 1:
        return await about_menu(session, level, menu_name)
    elif level == 2:
        return await contacts_menu(session, level, menu_name)
    elif level == 3:
        return await promos_menu(session, level, menu_name, page)
    elif level == 4:
        return await doctors_menu(session, level, menu_name, page)
    elif level == 5:
        return await calendar_menu(session, level, menu_name)
    elif level == 6:
        return await profile_menu(session, level, menu_name, user_id)
    elif level == 7:
        return await reception_history_menu(session, level, user_id, page, state)
    elif level == 8:
        return await visit_dates(session, level, user_id, page, state, doctor_id)
    elif level == 9:
        return await diagnosis_menu(session, level, user_id, state, date)
    elif level == 10:
        return await analysis_menu(session, level, page)
    elif level == 11:
        return await result_analysis_menu(session, level, user_id, specialty_id, page, state, per_page)


async def adm_main_menu(session, level, menu_name):
    banner = await models.orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_admin_menu_btns(level=level, sizes=(1, ))

    return image, kbds


async def get_menu_adm_content(
        session: AsyncSession,
        menu_name: str,
        level: int | None = None,
):
    if level == 0:
        return await adm_main_menu(session=session, menu_name=menu_name, level=level)
