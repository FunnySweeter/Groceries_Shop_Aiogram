from app.database.models import async_session, Admin
from app.database.models import User, Region, Item, Payment, Order
from sqlalchemy import select, update, delete
from datetime import datetime, date, time
import app.handlers as h


async def get_user_by_tg_id(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def set_user(tg_id):
    async with async_session() as session:
        user = await get_user_by_tg_id(tg_id)

        if not user:
            session.add(User(tg_id=tg_id, balance=0.0, reg_time=str(datetime.today())))
            await session.commit()


async def set_admin(tg_id, name, rights='0'):
    async with async_session() as session:
        admin = await session.scalar(select(Admin).where(Admin.tg_id == tg_id))

        if not admin:
            session.add(Admin(tg_id=tg_id, name=name, rights=rights, reg_time=str(datetime.today())))
            await session.commit()


async def get_all_admins():
    async with async_session() as session:
        return await session.scalars(select(Admin))


async def get_all_admins_id():
    async with async_session() as session:
        admins = await session.scalars(select(Admin))
        admins_id = []
        for admin in admins:
            admins_id.append(admin.id)
        return admins_id


async def get_regions():
    async with async_session() as session:
        return await session.scalars(select(Region))


async def get_region_name_by_id(region_id):
    async with async_session() as session:
        return await session.scalar(select(Region).where(Region.id == region_id))


async def get_region_item(region_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.region == region_id))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))


async def get_all_items():
    async with async_session() as session:
        return await session.scalars(select(Item))


async def add_payment(user_tg_id, text_id, amount):
    async with async_session() as session:
        session.add(Payment(
            user_tg_id=user_tg_id,
            text_id=text_id,
            amount=float(amount),
            success=False,
            time=str(datetime.today())
        ))
        await session.commit()


async def get_payment(user_tg_id, text_id):
    async with async_session() as session:
        return await session.scalar(
            select(Payment)
            .where(Payment.user_tg_id == user_tg_id)
            .where(Payment.text_id == text_id)
        )


async def check_payment(user_tg_id, text_id):
    async with async_session() as session:
        await session.execute(
            update(Payment)
            .where(Payment.user_tg_id == user_tg_id)
            .where(Payment.text_id == text_id)
            .values(time=str(datetime.today()))
        )
        await session.commit()