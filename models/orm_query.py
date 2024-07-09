import math
from datetime import datetime
from typing import Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import models


############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict):
    # Добавляем новый или изменяем существующий по именам
    # пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(models.Banners)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([models.Banners(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(models.Banners).where(models.Banners.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(models.Banners).where(models.Banners.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(models.Banners)
    result = await session.execute(query)
    return result.scalars().all()


# работа с акциями
async def orm_add_promo(session: AsyncSession, promo: dict):
    obj = models.Promo(promo_name=promo['promo_name'],
                       promo_description=promo['promo_description'],
                       promo_url=promo['promo_url'],
                       )
    session.add(obj)
    await session.commit()


async def orm_get_promos(session: AsyncSession):
    query = select(models.Promo)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_promo(session: AsyncSession, promo_name: str):
    query = select(models.Promo).where(models.Promo.promo_name == promo_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_promo(session: AsyncSession, promo_name: str, data: dict):
    query = (
        update(models.Promo)
        .where(models.Promo.promo_name == promo_name)
        .values(promo_name=data['promo_name'],
                promo_description=data['promo_description'],
                promo_url=data['promo_url'],
                )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_promo(session: AsyncSession, promo_name: str):
    query = delete(models.Promo).where(models.Promo.promo_name == promo_name)
    await session.execute(query)
    await session.commit()


async def orm_get_doctors(session: AsyncSession):
    query = select(models.Doctors)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_doctor(session: AsyncSession, doctor: dict):
    obj = models.Doctors(doctor_id=doctor['doctor_id'],
                         fio_doctor=doctor['fio_doctor'],
                         direction=doctor['direction'],
                         image=doctor.get('image', 'W:\\Чист\\Monitoring\\data\\image\\expert.webp')
                         )
    session.add(obj)
    await session.commit()


async def orm_get_banner_doctor(session: AsyncSession, doctor_id: int):
    query = select(models.Doctors).where(models.Doctors.doctor_id == doctor_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_add_user(
        session: AsyncSession,
        user_id: int,
        age: int,
        full_name: str | None = None,
        phone_number: str | None = None,
):
    query = select(models.Crm).where(models.Crm.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            models.Crm(user_id=user_id, age=age, full_name=full_name, phone_number=phone_number)
        )
        await session.commit()


async def orm_get_user_info(session: AsyncSession, user_id: int):
    query = select(models.Crm).where(models.Crm.user_id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()
    return user


async def orm_get_doctor_info(session: AsyncSession, doctor_id: int):
    query = select(models.Doctors).where(models.Doctors.doctor_id == doctor_id)
    result = await session.execute(query)
    user = result.scalars().first()
    return user


async def orm_add_request(session: AsyncSession, request: dict):
    obj = models.Applications(user_id=request['user_id'],
                              fio_client=request['fio_client'],
                              age_client=request['age_client'],
                              select_direction=request['select_direction'],
                              fio_doctor=request['fio_doctor'],
                              date=request['date'],
                              phone_number=request['phone_number']
                              )
    session.add(obj)
    await session.commit()


# получае fio по user_id
async def get_fio_by_user_id(session: AsyncSession, user_id: int) -> str:
    query = select(models.Crm.full_name).where(models.Crm.user_id == user_id)
    result = await session.execute(query)
    user_fio = result.scalar_one_or_none()
    return user_fio


# получаем список врачей у которых наш пользователь был на приёме
async def orm_get_reception_history_info(session: AsyncSession, user_id: int):
    fio_client = await get_fio_by_user_id(session=session, user_id=user_id)
    query = select(models.ReceptionHistory.fio_doctor, models.ReceptionHistory.date,
                   models.ReceptionHistory.diagnosis).where(models.ReceptionHistory.fio_client == fio_client)
    result = await session.execute(query)
    return result.fetchall()


async def orm_get_reception_history_date_info(session: AsyncSession, user_id: int, fio_doctor: str):
    fio_client = await get_fio_by_user_id(session=session, user_id=user_id)
    query = select(models.ReceptionHistory.date, models.ReceptionHistory.diagnosis).where(
        models.ReceptionHistory.fio_client == fio_client,
        models.ReceptionHistory.fio_doctor == fio_doctor)
    result = await session.execute(query)
    return result.fetchall()


async def orm_add_reception_history(session: AsyncSession, reception_history: dict):
    obj = models.ReceptionHistory(fio_client=reception_history['fio_client'],
                                  fio_doctor=reception_history['fio_doctor'],
                                  spec_doctor=reception_history['spec_doctor'],
                                  date=reception_history['date'],
                                  diagnosis=reception_history['diagnosis']
                                  )
    session.add(obj)
    await session.commit()


async def insert_specialty(session, name_specialty):
    new_specialty = models.Specialties(name_specialty=name_specialty)
    session.add(new_specialty)
    await session.commit()


async def get_id_doctor_by_fio(session: AsyncSession, fio_doctor: str) -> int:
    query = select(models.Doctors.id).where(models.Doctors.fio_doctor == fio_doctor)
    result = await session.execute(query)
    doctor_id = result.scalar_one_or_none()
    return doctor_id


# получаем ФИО врача и его id
async def get_doctors_fio_id(session: AsyncSession, user_id: int):
    query = (
        select(models.Doctors.fio_doctor, models.Doctors.id).join(models.ReceptionHistory,
                                                                  models.ReceptionHistory.fio_doctor == models.Doctors.fio_doctor).join(
            models.Crm,
            models.Crm.full_name == models.ReceptionHistory.fio_client).filter(models.Crm.user_id == user_id).distinct()
    )
    result = await session.execute(query)

    doctors = result.fetchall()
    return doctors


async def get_dates_by_user_id(session: AsyncSession, user_id: int, doctor_id: int):
    query = select(models.ReceptionHistory.date).join(models.Doctors,
                                                      models.ReceptionHistory.fio_doctor == models.Doctors.fio_doctor).join(
        models.Crm, models.ReceptionHistory.fio_client == models.Crm.full_name).filter(
        models.Doctors.doctor_id == doctor_id,
        models.Crm.user_id == user_id)

    result = await session.execute(query)

    dates = result.fetchall()
    return dates


async def get_dig_by_user_id(session: AsyncSession, user_id: int, doctor_id: int, date: str):
    date_object = datetime.strptime(date, "%d-%m-%Y")
    query = select(models.ReceptionHistory.diagnosis).join(models.Doctors,
                                                           models.ReceptionHistory.fio_doctor == models.Doctors.fio_doctor).join(
        models.Crm, models.ReceptionHistory.fio_client == models.Crm.full_name).filter(
        models.Doctors.doctor_id == doctor_id,
        models.Crm.user_id == user_id, models.ReceptionHistory.date == date_object)

    result = await session.execute(query)

    diagnosis = result.scalar_one_or_none()
    return diagnosis


async def get_name_specialty_id(session: AsyncSession):
    query = select(models.Specialties.name_specialty, models.Specialties.id)
    result = await session.execute(query)

    name_specialty_id = result.fetchall()

    return name_specialty_id


async def get_name_specialty_by_id(session: AsyncSession, specialty_id: int):
    query = select(models.Specialties.name_specialty).filter(models.Specialties.id == specialty_id)
    result = await session.execute(query)

    name_specialty = result.scalar_one_or_none()

    return name_specialty


async def get_analysis_file(session: AsyncSession, user_id: int, specialty_id: int):
    query = select(models.AnalysisHistory.analysis_file).filter(models.AnalysisHistory.user_id == user_id,
                                                                models.AnalysisHistory.specialty_id == specialty_id)

    result = await session.execute(query)

    result_file = result.scalar_one_or_none()

    return result_file


async def isAdmins(session: AsyncSession, user_id: int):
    query = select(models.Admins.user_id).filter(models.Admins.user_id == user_id)

    result = await session.execute(query)

    isAdmins = result.scalar_one_or_none()

    return False if isAdmins is None else True


async def isPatient(session: AsyncSession, user_id: int):
    query = select(models.Users.user_id).filter(models.Users.user_id == user_id)

    result = await session.execute(query)

    isPatient = result.scalar_one_or_none()

    return False if isPatient is None else True


async def update_text_hi(session, new_text: str):
    stmt = update(models.TextHi).where(models.TextHi.id == 1).values(text=new_text)
    await session.execute(stmt)
    await session.commit()


async def get_text_hi(session, text_id: int) -> str:
    stmt = select(models.TextHi).where(models.TextHi.id == text_id)
    result = await session.execute(stmt)

    string = result.scalar_one_or_none()

    return None if string is None else string.text


async def orm_get_users(session: AsyncSession):
    query = select(models.Crm.user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def getFormDataCrm(session: AsyncSession, user_id: int):
    # Создание запроса для поиска пользователя по user_id
    query = select(models.Crm).where(models.Crm.user_id == user_id)
    # Выполнение запроса
    result = await session.execute(query)
    # Извлечение первой строки результата
    user = result.scalars().first()
    return user


async def insert_user(session: AsyncSession, user_id: int):
    new_user = models.Users(user_id=user_id)
    session.add(new_user)
    await session.commit()


async def orm_get_users_start(session: AsyncSession):
    query = select(models.Users.user_id)
    result = await session.execute(query)
    return result.scalars().all()
