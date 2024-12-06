import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.types import Message, BotCommand, BotCommandScopeDefault
from aiogram.filters import CommandStart, Command

from decouple import config

from app.handlers.admin import router_admin
from app.handlers.user import router_user

from app.database.models import async_main
import app.database.requests as rq


bot = Bot(token=config('TOKEN'), default=DefaultBotProperties())


async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    await async_main()
    # count_users = await get_all_users(count=True)
    # try:
    #     for admin_id in admins:
    #         await bot.send_message(admin_id, f'Я запущен🥳. Сейчас в базе данных <b>{count_users}</b> пользователей.')
    # except:
    #     pass


async def stop_bot():
    # try:
    #     for admin_id in admins:
    #         await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    # except:
    #     pass
    pass


async def main():
    dp = Dispatcher()

    dp.include_router(router_admin)
    dp.include_router(router_user)

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        print("Попытка выключения бота...")
        await bot.session.close()
        print("Бот выключен")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Была команда на выключение')