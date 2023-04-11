"""Keyboards module for Schedule Telegram bot"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class Keyboards:
    """
    Class of keyboards for user
    """
    
    @staticmethod
    def get_start_kb() -> ReplyKeyboardMarkup:
        """
        Returns initial keyboard

        Returns:
            ReplyKeyboardMarkup
        """
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('/help')]
        ], resize_keyboard=True)
        return kb

    @staticmethod
    def get_cancel_kb() -> ReplyKeyboardMarkup:
        """
        Returns keyboard for final state

        Returns:
            ReplyKeyboardMarkup
        """
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('Расписание на сегодня  ▶️')],
            [KeyboardButton('Расписание на завтра  ⏩')],
            [KeyboardButton('Расписание на неделю  ⏭')],
            [KeyboardButton('Вернуться назад  ↩️')]
        ], resize_keyboard=True)
        return kb
