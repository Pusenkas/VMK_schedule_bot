from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton('/help'),
         KeyboardButton('/schedule')]
    ], resize_keyboard=True)
    return kb


def get_schedule_option_kb() -> ReplyKeyboardMarkup:
	kb = ReplyKeyboardMarkup(keyboard=[
		[KeyboardButton('/today_schedule'),
		 KeyboardButton('/week_schedule')]
	], resize_keyboard=True)
	return kb


def get_cancel_kb() -> ReplyKeyboardMarkup:
	kb = ReplyKeyboardMarkup(keyboard=[
		[KeyboardButton('/return_to_menu'),
		 KeyboardButton('/change_group_number')]
	], resize_keyboard=True)
	return kb
