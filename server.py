from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from keyboards import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class StudentGroupState(StatesGroup):
    processing = State()
    group_number = State()
    option_proccesing = State()
    today_schedule = State()
    week_schedule = State()
    dump = State()


async def on_startup(_) -> None:
    print('Bot has been started')


async def cmd_schedule(message: types.Message, reply_markup: ReplyKeyboardMarkup) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите номер вашей учебной группы',
                           reply_markup=reply_markup)


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать!\n'
                                'Я бот, отправляющий расписание ВМК',
                           reply_markup=get_start_kb())
    await StudentGroupState.processing.set()


@dp.message_handler(commands=['help'], state='*')
async def cmd_help(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='/start - начать работу с ботом\n'
                                '/help - получить подсказки по командам\n'
                                '/schedule - получить расписание')


@dp.message_handler(commands=['schedule'], state=StudentGroupState.processing)
async def handle_schedule_while_processing(message: types.Message) -> None:
    await cmd_schedule(message, reply_markup=get_start_kb())
    await StudentGroupState.group_number.set()


@dp.message_handler(commands=['schedule'], state=[StudentGroupState.group_number, StudentGroupState.option_proccesing])
async def handle_schedule_while_number(message: types.Message) -> None:
    await cmd_schedule(message, reply_markup=get_start_kb())
    await StudentGroupState.group_number.set()


@dp.message_handler(commands=['today_schedule'], state=StudentGroupState.option_proccesing)
async def cmd_today_schedule(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Держите ваше расписание на сегодня',
                           reply_markup=get_cancel_kb())
    await StudentGroupState.dump.set()


@dp.message_handler(commands=['return_to_menu'], state=StudentGroupState.dump)
async def cmd_cancel(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Вы вернулись в главное меню',
                           reply_markup=get_start_kb())
    await StudentGroupState.processing.set()


@dp.message_handler(commands=['change_group_number'], state=StudentGroupState.dump)
async def cmd_change(message: types.Message, state: FSMContext) -> None:
    await cmd_schedule(message, reply_markup=get_start_kb())
    await StudentGroupState.group_number.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=StudentGroupState.group_number)
async def handle_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['number'] = message.text
    await bot.send_message(chat_id=message.from_user.id,
                           text='Выберите опцию',
                           reply_markup=get_schedule_option_kb())
    await StudentGroupState.option_proccesing.set()


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


@dp.message_handler(state=StudentGroupState.option_proccesing)
async def handle_message_while_opt(message: types.Message, state: FSMContext) -> None:
    await message.reply(text='Выберите одну из предложенных опций',
                        reply_markup=get_schedule_option_kb())


@dp.message_handler(state=StudentGroupState.processing)
async def handle_message_while_processing(message: types.Message, state: FSMContext) -> None:
    await message.reply(text='Выберите одну из предложенных опций',
                        reply_markup=get_start_kb())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, 
                           skip_updates=True, 
                           on_startup=on_startup)
