import asyncio
import time

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.fsm import state
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Chat, User
from aiogram.filters import CommandStart, Command, CommandObject

from decouple import config

import app.keyboards as kb
import app.database.requests as rq
from app.utils import get_hash

CARD_NUMBER = config('CARD_NUMBER')
ID_PREFIX = config('ID_PREFIX')

router_user = Router()


class CurrentBotMessage(StatesGroup):
    msg = State()
    region = State()
    add_money_to_balance = State()
    typed_money = State()
    main_state = State()
    admins_chats = State()
    test = State()


@router_user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await rq.set_user(message.from_user.id)
    await message.answer('Добро пожаловать в шоп Triangle.')
    await state.update_data(msg=await message.answer('Выберите пункт меню.', reply_markup=kb.main))
    # if message.from_user.id in
    await state.update_data({'admins_chats': []})
    await state.set_state(CurrentBotMessage.main_state)


@router_user.message(F.text == 'Профиль')
async def profile(message: Message, state: FSMContext):
    await message.answer('Ваш профиль\n\nБаланс: 0.00 руб.\n\nКол-во заказов: 0\nСумма заказов: 0.00 руб.', reply_markup=kb.profile)


@router_user.message(F.text == 'На главную')
async def to_main(message: Message, state: FSMContext):
    await state.update_data(msg=await message.answer('Выберите пункт меню.', reply_markup=kb.main))


@router_user.message(F.text == 'Каталог')
async def catalog(message: Message, state: FSMContext):
    # await state.update_data(msg=await message.answer('...', reply_markup=types.ReplyKeyboardRemove()))
    # data = await state.get_data()
    # await data["msg"].delete()

    await state.update_data(msg=await message.answer('Выберите район', reply_markup=await kb.regions()))


@router_user.callback_query(F.data.startswith('region_'))
async def region_(callback: CallbackQuery, state: FSMContext):
    region_name = await rq.get_region_name_by_id(callback.data.split('_')[1])
    # await callback.answer(f'Выбран регион {region_name.name}')

    await state.update_data(region=callback.data.split('_')[1])
    data = await state.get_data()
    # await data["msg"].delete()

    all_items = await rq.get_region_item(callback.data.split('_')[1])
    items_count = 0
    is_empty = ''
    for item in all_items: items_count += 1
    if items_count <= 0:
        is_empty = f"{region_name.name} район.\n\nВитрина пуста."
    else:
        is_empty = f"{region_name.name} район."
    await data["msg"].edit_text(f'{is_empty}', reply_markup=await kb.items(callback.data.split('_')[1]))
    # await state.update_data(msg=await callback.message.answer('Выберите товар', reply_markup=await kb.items(callback.data.split('_')[1])))


@router_user.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await data["msg"].delete()
    await state.update_data(msg=await callback.message.answer('Выберите пункт меню.', reply_markup=kb.main))


@router_user.callback_query(F.data == 'back_to_regions')
async def back_to_regions(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await data["msg"].edit_text('Выберите район', reply_markup=await kb.regions())


@router_user.callback_query(F.data.startswith('item_'))
async def item_(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_data = await rq.get_item(callback.data.split('_')[1])
    # await callback.answer('Товар выбран')
    await data["msg"].edit_text(f'Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price} рублей', reply_markup=await kb.item_menu(callback.data.split('_')[1], item_data.price))


@router_user.callback_query(F.data == 'back_to_items')
async def back_to_items(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    region_name = await rq.get_region_name_by_id(data["region"])
    # await data["msg"].delete()

    all_items = await rq.get_region_item(data["region"])
    items_count = 0
    is_empty = ''
    for item in all_items: items_count += 1
    if items_count <= 0:
        is_empty = f"{region_name.name} район.\n\nВитрина пуста."
    else:
        is_empty = f"{region_name.name} район."
    await data["msg"].edit_text(f'{is_empty}', reply_markup=await kb.items(data["region"]))


@router_user.message(F.text == 'Пополнить баланс')
async def add_money_to_balance(message: Message, state: FSMContext):
    await state.set_state(CurrentBotMessage.add_money_to_balance)
    await message.answer('Введите сумму пополнения', reply_markup=kb.cancel_add_money)

@router_user.message(CurrentBotMessage.add_money_to_balance, F.text)
async def add_money_to_balance(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer('Операция прервана', reply_markup=kb.main)
        await state.set_state(CurrentBotMessage.main_state)
    else:
        await message.answer('Выберите способ оплаты', reply_markup=await kb.select_payment_method())
        await state.update_data(typed_money=message.text)

@router_user.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    await message.answer('Операция прервана', reply_markup=kb.main)
    await state.set_state(CurrentBotMessage.main_state)

@router_user.callback_query(CurrentBotMessage.add_money_to_balance, F.data)
async def transfer_to_card(callback: CallbackQuery, state: FSMContext, bot: Bot):

    if callback.data == 'transfer_to_card':
        data = await state.get_data()

        # payment_text_id = list()
        # payment_text_id.append(ID_PREFIX)
        c_time = list(''.join(str(time.time()).split('.')))
        c_time.pop(0)

        # while len(c_time) > 0:
        #     bar = 0
        #     bar2 = list()
        #     bar += int(c_time.pop(0)) + 1
        #     if len(c_time) >= 1:
        #         bar *= int(c_time.pop())
        #     if len(c_time) >= 1:
        #         bar2.append(c_time.pop())
        #         if len(c_time) >= 1:
        #             bar2.append(c_time.pop(0))
        #         bar *= int(''.join(bar2))
        #     if len(c_time) >= 1:
        #         bar -= int(c_time.pop())
        #         if bar < 0:
        #             bar *= -1
        #     payment_text_id.append(f'-{bar}')
        #
        # payment_text_id = ''.join(payment_text_id)

        payment_text_id = get_hash(prefix=ID_PREFIX, series_of_numbers=c_time)

        await callback.message.answer(f'Перевод на карту.\n\nДля продолжения, переведите {data["typed_money"]} руб. по номеру карты:\n{CARD_NUMBER}\n\nЗачисления проверяются администратором вручную, в средем это занимает 5-20 минут.\n\nID платежа: {payment_text_id}', reply_markup=await kb.im_paid(payment_text_id))
        await rq.add_payment(user_tg_id=callback.from_user.id, text_id=payment_text_id, amount=data["typed_money"])

    if callback.data.startswith('im_paid_'):

        payment_text_id = callback.data.split('_')[-1]
        print(payment_text_id)
        admins = await rq.get_all_admins()
        await rq.check_payment(user_tg_id=callback.from_user.id, text_id=payment_text_id)
        payment = await rq.get_payment(user_tg_id=callback.from_user.id, text_id=payment_text_id)

        p_time = payment.time.split(".")
        p_time.pop()
        p_time = ''.join(p_time)

        text_status = 'Подтверждено' if payment.success else 'Ожидает подтверждения'

        txt = f'User {callback.from_user.id} нажал кнопку "Я оплатил"\n\n' \
              f'' \
              f'Дата и время: {p_time}\n' \
              f'Сумма: {payment.amount} руб.\n\n' \
              f'' \
              f'Статус: {text_status}'

        data = await state.get_data()
        await state.update_data({'admins_chats': data['admins_chats']})

        for admin in admins:
            msg = await bot.send_message(chat_id=admin.tg_id, text=txt, reply_markup=await kb.confirm_payment_by_admin(payment_text_id))
            await state.update_data({'admins_chats': data['admins_chats'].append({'payment_text_id': payment_text_id,
                                                                                  'message_id': msg.message_id,
                                                                                  'chat_id': admin.tg_id})})

        if callback.data.startswith('confirmed_pay_'):

            payment_text_id = callback.data.split('_')[-1]

            # bot.edit_message_text(message_id=)
            # TODO: 0000000000000000000000000000000000000


@router_user.message(F.text == 'admin:4%6wNj206#%P5OD(')
async def admin_mode(message: Message, state: FSMContext):
    await message.answer('Режим администратора.', reply_markup=await kb.admin_main())
    await rq.set_admin(tg_id=message.from_user.id, rights='check_payments', name='admin')
    # await state.update_data(admins_chats=444555)
    # print(CurrentBotMessage.admins_chats)

    # msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="ТЕКСТ", parse_mode='Markdown')
    # msg = bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=ModeKeyboard)





@router_user.message(Command('test'))
async def test(message: Message, state: FSMContext, bot: Bot):
    # await state.update_data(test=await message.answer('Test 111'))
    # data = await state.get_data()
    # print(data['test'])

    # await bot.edit_message_text(text='test!', chat_id=message.from_user.id, message_id=1762)
    # РАБОТАЕТ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    admins = await rq.get_all_admins()
    for admin in admins:
        await bot.send_message(chat_id=admin.tg_id, text=f'Test work')

    # data['admins_chats'].append(1)
    # print(data['admins_chats'])