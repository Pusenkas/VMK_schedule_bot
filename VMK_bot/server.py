"""Server side for Schedule Telegram bot."""

import asyncio
from VMK_bot.messageUI import MessageToUser
from VMK_bot.keyboards import Keyboards
from VMK_bot.database import Database
from aiogram import Bot, Dispatcher, executor, types
from VMK_bot.config import TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler
import datetime
from VMK_bot.pdf_parser import Parser


bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database()


class StudentGroupState(StatesGroup):
    """FSM (Finite State Machine) of user's states and transitions between them.

    Args:
        processing (State): initial state where user can send group number
        final (State): user is supposed to choose between returning to menu,
                      changing the group number or choose to look at today/week schedule
        STATES (dict['str':State]): "map" between string repr of state and its actual mark
    """

    processing = State()
    final = State()

    STATES = {
        'processing': processing,
        'final': final
    }


class StateMiddleware(BaseMiddleware):
    """State's Middleware (stage between request is sent to bot and its actual processing by handler).

    Puts user's FSM in the state where user left it
    This concept makes bot independent of shutdowns on its side
    """

    @staticmethod
    async def on_pre_process_message(message: types.Message, data: dict) -> None:
        """Method to set user's FSM in the last state.

        Args:
            message (types.Message): message from user
            data (dict): namespace
        """
        username = message.from_user.username
        user_state = db.get_user_state(username)
        cur_state = StudentGroupState.STATES[user_state]
        await cur_state.set()


class ThrottlingMiddleware(BaseMiddleware):
    """Antiflood Middleware."""

    def __init__(self, rate_limit: int = 0.5):
        """Initializes the object's attributes.

        Args:
            rate_limit (int): limit (in seconds) for messages/second
        """
        BaseMiddleware.__init__(self)
        self.rate_limit = rate_limit

    async def on_process_message(self, message: types.Message, data: dict) -> None:
        """Method to interrupt processing new message if limit exceeded.

        Args:
            message (types.Message): message from user
            data (dict): namespace
        """
        dp = Dispatcher.get_current()

        try:
            await dp.throttle(key='antiflood_message', rate=self.rate_limit)
        except Throttled as _t:
            await self.msg_throttle(message, _t)
            raise CancelHandler()

    @staticmethod
    async def msg_throttle(message: types.Message, throttled: Throttled) -> None:
        """Method to send a message to user that he's exceeded limit for messages.

        Args:
            message (types.Message): message from user
            throttled (Throttled): an exception caused by limit's exceeding
        """
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            message_to_user = MessageToUser.translate('Вы превысили лимит сообщений. Подождите',
                                                      message.from_user.language_code)
            await message.reply(message_to_user)
        await asyncio.sleep(delta)


async def on_startup(_) -> None:
    """Executes on bot's startup.

    Should connect to the users database
    """
    db.connect()
    print('Bot has been started')


async def set_state(state: FSMContext, new_state: str, message: types.Message) -> None:
    """Sets FSM in a specific state.

    Args:
        state (FSMContext): significant to open proxy and write state into it
        new_state (str): string repr of state to be set
        message (types.Message): message of user
    """
    async with state.proxy() as data:
        data['state'] = new_state

    await db.edit_user_state(state, message.from_user.username)
    await StudentGroupState.STATES[new_state].set()


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Handler of command 'start' from user in any state.

    Sends start message to user

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    message_to_user = MessageToUser.translate('Добро пожаловать!\nЯ бот, отправляющий расписание ВМК',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user,
                           reply_markup=Keyboards.get_start_kb(message.from_user.language_code))

    message_to_user = MessageToUser.translate('Для получения расписания введите номер вашей учебной группы',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user,
                           reply_markup=Keyboards.get_start_kb(message.from_user.language_code))

    db.add_user(message.from_user.username)
    await set_state(state, 'processing', message)


@dp.message_handler(commands=['help'], state='*')
async def cmd_help(message: types.Message) -> None:
    """Handler of command 'help' from user in any state.

    Sends help message to user

    Args:
        message (types.Message): message from user
    """
    message_to_user = MessageToUser.translate('/start - начать работу с ботом\n/help - получить подсказки по командам',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user)


@dp.message_handler(lambda message: message.text == MessageToUser.translate('Расписание на сегодня  ▶️', message.from_user.language_code),
                    state=StudentGroupState.final)
async def cmd_today_schedule(message: types.Message, state: FSMContext) -> None:
    """Handler of command today_schedule from user in final state.

    Sends today's schedule to user

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    week = datetime.datetime.today().isocalendar()[1]
    day = datetime.datetime.today().weekday()
    group_number = db.get_user_group(message.from_user.username)
    schedule = Parser.get_today_schedule(group_number, week % 2, Parser.number_to_weekday(day))

    message_to_user = MessageToUser.translate('Держите ваше расписание на сегодня\n',
                                              message.from_user.language_code)

    schedule = message_to_user + schedule
    await bot.send_message(chat_id=message.from_user.id,
                           text=schedule, parse_mode='HTML',
                           reply_markup=Keyboards.get_cancel_kb(message.from_user.language_code))


@dp.message_handler(lambda message: message.text == MessageToUser.translate('Расписание на неделю  ⏭', message.from_user.language_code),
                    state=StudentGroupState.final)
async def cmd_week_schedule(message: types.Message, state: FSMContext) -> None:
    """Handler of command week_schedule from user in final state.

    Sends week's schedule to user

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    week = datetime.datetime.today().isocalendar()[1]
    group_number = db.get_user_group(message.from_user.username)
    schedule = Parser.get_week_schedule(group_number, week % 2)

    message_to_user = MessageToUser.translate('Держите ваше расписание на неделю\n',
                                              message.from_user.language_code)

    schedule = message_to_user + schedule
    await bot.send_message(chat_id=message.from_user.id,
                           text=schedule, parse_mode='HTML',
                           reply_markup=Keyboards.get_cancel_kb(message.from_user.language_code))


@dp.message_handler(lambda message: message.text == MessageToUser.translate('Расписание на завтра  ⏩', message.from_user.language_code),
                    state=StudentGroupState.final)
async def cmd_tomorrow_schedule(message: types.Message, state: FSMContext) -> None:
    """Handler of command tomorrow_schedule from user in final state.

    Sends tomorrow's schedule to user

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    week = tomorrow.isocalendar()[1]
    day = tomorrow.weekday()
    group_number = db.get_user_group(message.from_user.username)
    schedule = Parser.get_today_schedule(group_number, week % 2, Parser.number_to_weekday(day))

    message_to_user = MessageToUser.translate('Держите ваше расписание на завтра\n',
                                              message.from_user.language_code)

    schedule = message_to_user + schedule
    await bot.send_message(chat_id=message.from_user.id,
                           text=schedule, parse_mode='HTML',
                           reply_markup=Keyboards.get_cancel_kb(message.from_user.language_code))


@dp.message_handler(lambda message: message.text == MessageToUser.translate('Вернуться назад  ↩️', message.from_user.language_code),
                    state=StudentGroupState.final)
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    """Handler of command return_to_menu from user in final state.

    Sets FSM to initial state

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    message_to_user = MessageToUser.translate('Вы вернулись в главное меню',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user,
                           reply_markup=Keyboards.get_start_kb(message.from_user.language_code))

    message_to_user = MessageToUser.translate('Для получения расписания введите номер вашей учебной группы',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user,
                           reply_markup=Keyboards.get_start_kb(message.from_user.language_code))
    await set_state(state, 'processing', message)


@dp.message_handler(lambda message: message.text in db.get_valid_groups(),
                    state=StudentGroupState.processing)
async def handle_number(message: types.Message, state: FSMContext) -> None:
    """Handler of group number from user in initial state.

    Stores number in state.proxy, edits database with new group for user,
    sets FSM to final state and sends Option Keyboard to user

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    async with state.proxy() as data:
        data['group'] = message.text

    await db.edit_user_group(state, username=message.from_user.username)

    message_to_user = MessageToUser.translate('Выберите опцию!',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user,
                           reply_markup=Keyboards.get_cancel_kb(message.from_user.language_code))
    await set_state(state, 'final', message)


@dp.message_handler(lambda message: message.text not in db.get_valid_groups(),
                    state=StudentGroupState.processing)
async def handle_wrong_number(message: types.Message, state: FSMContext) -> None:
    """Handler of wrong group number from user in initial state.

    Replies to user's message notifying that it's a wrong number

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    message_to_user = MessageToUser.translate('Неверный номер группы!\nПовторите попытку',
                                              message.from_user.language_code)
    await message.reply(text=message_to_user,
                        reply_markup=Keyboards.get_start_kb(message.from_user.language_code))


@dp.message_handler(state=StudentGroupState.final)
async def handle_message_while_final(message: types.Message, state: FSMContext) -> None:
    """Handler of any message from user in final state.

    Returns message that this is a wrong command and option is needed to be chosen

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    message_to_user = MessageToUser.translate('Выберите опцию!',
                                              message.from_user.language_code)
    await bot.send_message(chat_id=message.from_user.id,
                           text=message_to_user,
                           reply_markup=Keyboards.get_cancel_kb(message.from_user.language_code))


@dp.message_handler(state=StudentGroupState.processing)
async def handle_message_while_processing(message: types.Message, state: FSMContext) -> None:
    """Handler of any message from user in initial state.

    Replies that this is a wrong command and suggested option was expected

    Args:
        message (types.Message): message from user
        state (FSMContext): state of user
    """
    message_to_user = MessageToUser.translate('Выберите опцию!',
                                              message.from_user.language_code)
    await message.reply(text=message_to_user,
                        reply_markup=Keyboards.get_start_kb(message.from_user.language_code))


def run_server():
    """Runs server logic."""
    dp.middleware.setup(StateMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())

    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)


if __name__ == '__main__':
    run_server()
