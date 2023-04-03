from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from keyboards import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from database import db_connect, add_user, edit_user_group, edit_user_state, get_user_state
from aiogram.dispatcher.middlewares import BaseMiddleware


bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class StudentGroupState(StatesGroup):

    processing = State()
    group_number = State()
    option_processing = State()
    today_schedule = State()
    week_schedule = State()
    dump = State()

    STATES = {
              'processing': processing, 
              'group_number': group_number,
              'option_processing': option_processing,
              'today_schedule': today_schedule,
              'week_schedule': week_schedule,
              'dump': dump
             }


class StateMiddleware(BaseMiddleware):

    async def on_pre_process_message(self, message: types.Message, data: dict) -> None:
        username = message.from_user.username
        setattr(StudentGroupState, 'username', username)
        user_state = await get_user_state(username)
        cur_state = StudentGroupState.STATES[user_state]
        await cur_state.set()


async def on_startup(_) -> None:
    await db_connect()
    print('Bot has been started')


async def set_state(state: FSMContext, new_state: str) -> None:
    async with state.proxy() as data:
        data['state'] = new_state
        username = StudentGroupState.username
        
    await edit_user_state(state, username)
    await StudentGroupState.STATES[new_state].set()


async def cmd_schedule(message: types.Message, reply_markup: ReplyKeyboardMarkup) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите номер вашей учебной группы',
                           reply_markup=reply_markup)


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать!\n'
                                'Я бот, отправляющий расписание ВМК',
                           reply_markup=get_start_kb())

    await add_user(username=message.from_user.username)
    await set_state(state, 'processing')


@dp.message_handler(commands=['help'], state='*')
async def cmd_help(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='/start - начать работу с ботом\n'
                                '/help - получить подсказки по командам\n'
                                '/schedule - получить расписание')


@dp.message_handler(commands=['schedule'], state=[StudentGroupState.group_number, 
                                                  StudentGroupState.option_processing, 
                                                  StudentGroupState.processing])
async def handle_schedule_while_number(message: types.Message, state: FSMContext) -> None:
    await cmd_schedule(message, reply_markup=get_start_kb())
    await set_state(state, 'group_number')


@dp.message_handler(commands=['today_schedule'], state=StudentGroupState.option_processing)
async def cmd_today_schedule(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Держите ваше расписание на сегодня',
                           reply_markup=get_cancel_kb())
    await set_state(state, 'dump')


@dp.message_handler(commands=['week_schedule'], state=StudentGroupState.option_processing)
async def cmd_week_schedule(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                            text='Держите ваше расписание на неделю',
                            reply_markup=get_cancel_kb())
    await set_state(state, 'dump')


@dp.message_handler(commands=['return_to_menu'], state=StudentGroupState.dump)
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Вы вернулись в главное меню',
                           reply_markup=get_start_kb())
    await set_state(state, 'processing')


@dp.message_handler(commands=['change_group_number'], state=StudentGroupState.dump)
async def cmd_change(message: types.Message, state: FSMContext) -> None:
    await cmd_schedule(message, reply_markup=get_start_kb())
    await set_state(state, 'group_number')


@dp.message_handler(lambda message: message.text.isdigit(), state=StudentGroupState.group_number)
async def handle_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['group'] = message.text

    await edit_user_group(state, username=message.from_user.username)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите опцию',
                           reply_markup=get_schedule_option_kb())
    await set_state(state, 'option_processing')


@dp.message_handler(lambda message: not message.text.isdigit(), state=StudentGroupState.group_number)
async def handle_wrong_number(message: types.Message, state: FSMContext) -> None:
    await message.reply(text='Неверный номер группы!\n'
                             'Повторите попытку',
                        reply_markup=get_start_kb())


@dp.message_handler(state=StudentGroupState.dump)
async def handle_message_while_dump(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите опцию!',
                           reply_markup=get_cancel_kb())


@dp.message_handler(state=StudentGroupState.option_processing)
async def handle_message_while_opt(message: types.Message, state: FSMContext) -> None:
    await message.reply(text='Выберите одну из предложенных опций',
                        reply_markup=get_schedule_option_kb())


@dp.message_handler(state=StudentGroupState.processing)
async def handle_message_while_processing(message: types.Message, state: FSMContext) -> None:
    await message.reply(text='Выберите одну из предложенных опций',
                        reply_markup=get_start_kb())


if __name__ == '__main__':
    dp.middleware.setup(StateMiddleware())

    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)
