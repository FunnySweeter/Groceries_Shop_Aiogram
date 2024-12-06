from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.requests import get_regions, get_region_item, get_all_items
from aiogram.utils.keyboard import InlineKeyboardBuilder


main = ReplyKeyboardMarkup(
    keyboard=
    [
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Каталог')],
        [KeyboardButton(text='Поддержка'), KeyboardButton(text='Правила')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)


profile = ReplyKeyboardMarkup(
    keyboard=
    [
        [KeyboardButton(text='Пополнить баланс')],
        [KeyboardButton(text='История заказов')],
        [KeyboardButton(text='На главную')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)


cancel_add_money = ReplyKeyboardMarkup(
    keyboard=
    [
        [KeyboardButton(text='Отмена')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Введите сумму пополнения...'
)


async def select_payment_method():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Перевод на карту', callback_data='transfer_to_card'))
    return keyboard.adjust(1).as_markup()


async def im_paid(payment_text_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Я оплатил', callback_data=f'im_paid_{payment_text_id}'))
    print('кнопка создана')
    return keyboard.adjust(1).as_markup()


async def admin_main():
    all_items = await get_all_items()
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def confirm_payment_by_admin(payment_text_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Подтвердить', callback_data=f'confirmed_pay_{payment_text_id}'))
    return keyboard.adjust(1).as_markup()


async def regions():
    all_regions = await get_regions()
    keyboard = InlineKeyboardBuilder()
    for region in all_regions:
        keyboard.add(InlineKeyboardButton(text=region.name, callback_data=f"region_{region.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def items(region_id):
    all_items = await get_region_item(region_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
    keyboard.row(
        InlineKeyboardButton(text=f'Назад', callback_data='back_to_regions'),
        InlineKeyboardButton(text=f'На главную', callback_data='to_main'),
        width=2
    )
    return keyboard.adjust(1).as_markup()


async def item_menu(item_id, price):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=f'Купить ({price} руб.)', callback_data=f"__________________"))
    keyboard.row(
        InlineKeyboardButton(text=f'Назад', callback_data='back_to_items'),
        InlineKeyboardButton(text=f'На главную', callback_data='to_main')
    )
    return keyboard.adjust(1).as_markup()