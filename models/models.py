from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, DateTime, func, String, ForeignKey


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class TextHi(Base):
    __tablename__ = 'TextHi'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text)

# CRM
class Crm(Base):
    __tablename__ = 'Crm'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=True)
    phone_number: Mapped[str] = mapped_column(Text, nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)

class Users(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=True)


# список акций
class Promo(Base):
    __tablename__ = 'Promo'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    promo_name: Mapped[str] = mapped_column(Text, unique=True, nullable=True)
    promo_description: Mapped[str] = mapped_column(Text, nullable=True)
    promo_url: Mapped[str] = mapped_column(Text, nullable=True)


# список Врачей
class Doctors(Base):
    __tablename__ = 'Doctors'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    fio_doctor: Mapped[str] = mapped_column(Text, nullable=True)
    direction: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True,
                                       server_default='W:\Чист\Monitoring\data\image\expert.webp')


# список направлений
class Directions(Base):
    __tablename__ = 'Directions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    direction_name: Mapped[str] = mapped_column(Text, unique=True, nullable=True)


# список заявок
class Applications(Base):
    __tablename__ = 'Applications'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    fio_client: Mapped[str] = mapped_column(Text, nullable=True)
    age_client: Mapped[int] = mapped_column(nullable=True)
    select_direction: Mapped[str] = mapped_column(Text, nullable=True)
    fio_doctor: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime)
    phone_number: Mapped[str] = mapped_column(Text, nullable=True)


# список Админов
class Admins(Base):
    __tablename__ = 'Admins'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=True)


# Картинок и их описания
class Banners(Base):
    __tablename__ = 'Banners'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


# История приёмов
class ReceptionHistory(Base):
    __tablename__ = 'ReceptionHistory'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fio_client: Mapped[str] = mapped_column(Text, nullable=True)
    fio_doctor: Mapped[str] = mapped_column(Text, nullable=True)
    spec_doctor: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=True)


class Specialties(Base):
    __tablename__ = 'Specialties'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_specialty: Mapped[str] = mapped_column(Text, nullable=True)


class AnalysisHistory(Base):
    __tablename__ = 'AnalysisHistory'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    specialty_id: Mapped[int] = mapped_column(ForeignKey('Specialties.id'))
    user_id: Mapped[int] = mapped_column(nullable=True)
    fio_client: Mapped[str] = mapped_column(Text, nullable=True)
    analysis_file: Mapped[str] = mapped_column(Text, nullable=True)
