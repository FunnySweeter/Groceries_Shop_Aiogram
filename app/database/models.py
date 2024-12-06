from aiogram.methods import set_my_default_administrator_rights
from sqlalchemy import BigInteger, String, ForeignKey, FLOAT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

engine = create_async_engine(url='sqlite+aiosqlite:///app/database/db.sqlite3')

# async_session = AsyncSession(engine, expire_on_commit=False)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    # id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, primary_key=True)
    balance: Mapped[float] = mapped_column()
    reg_time: Mapped[str] = mapped_column(String(50))


class Admin(Base):
    __tablename__ = 'admins'

    # id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), default='0', server_default='0')
    rights: Mapped[str] = mapped_column(String(100), default='0', server_default='0')
    reg_time: Mapped[str] = mapped_column(String(50))


class Region(Base):
    __tablename__ = 'regions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    # tg_id = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column()
    region: Mapped[int] = mapped_column(ForeignKey('regions.id'))
    coordinates: Mapped[str] = mapped_column(String(50))
    active_offer: Mapped[bool] = mapped_column()


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    text_id: Mapped[str] = mapped_column(String(30))
    amount: Mapped[float] = mapped_column()
    success: Mapped[bool] = mapped_column()
    time: Mapped[str] = mapped_column(String(50))


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    text_id: Mapped[str] = mapped_column(String(30))
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    success: Mapped[bool] = mapped_column()
    time: Mapped[str] = mapped_column(String(50))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)