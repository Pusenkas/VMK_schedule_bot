from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from keyboards import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from pdf_parser import Parser

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class StudentStateGroup(StatesGroup):
    processing = State()
    group_number = State()


async def cmd_schedule(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите номер вашей учебной группы')

    await StudentStateGroup.group_number.set()


async def on_startup(_):
    print('Bot has been started')


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать!\n'
                                'Я бот, отправляющий расписание ВМК',
                           reply_markup=get_start_kb())

    await StudentStateGroup.processing.set()


@dp.message_handler(commands=['help'], state='*')
async def cmd_help(message: types.Message) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text='/start - начать работу с ботом\n'
                                '/help - получить подсказки по командам\n'
                                '/schedule - получить расписание')


@dp.message_handler(commands=['schedule'], state=StudentStateGroup.processing)
async def schedule_wrapper(message: types.Message) -> None:
    await cmd_schedule(message)
    await StudentStateGroup.group_number.set()


@dp.message_handler(commands=['schedule'], state=StudentStateGroup.group_number)
async def handle_schedule_while_state(message: types.Message, state: FSMContext) -> None:
    await cmd_schedule(message)


@dp.message_handler(lambda message: message.text.isdigit(), state=StudentStateGroup.group_number)
async def handle_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['number'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text='Держите ваше расписание!')
    await bot.send_message(chat_id=message.from_user.id, text=Parser.get_lesson_from_json("data.json", message.text))
    await StudentStateGroup.processing.set()


@dp.message_handler(lambda message: not message.text.isdigit(), state=StudentStateGroup.group_number)
async def handle_wrong_number(message: types.Message, state: FSMContext) -> None:
    await message.reply('Неверный номер группы!\n'
                        'Отправьте номер заново')


if __name__ == '__main__':
    Parser.pdf_to_json("example.pdf", "data.json")

    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
