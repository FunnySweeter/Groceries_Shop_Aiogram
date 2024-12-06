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
import app.utils

CARD_NUMBER = config('CARD_NUMBER')
ID_PREFIX = config('ID_PREFIX')

router_admin = Router()