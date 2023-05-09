"""Keyboards module for Schedule Telegram bot"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from VMK_bot.messageUI import MessageToUser


class Keyboards:
    """
    Class of keyboards for user
    """
    @staticmethod
    def get_start_kb(language: str) -> ReplyKeyboardMarkup:
        """
        Returns initial keyboard

        Args:
            language (str): user's language
        Returns:
            ReplyKeyboardMarkup
        """
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('/help')]
        ], resize_keyboard=True)
        return kb

    @staticmethod
    def get_cancel_kb(language: str) -> ReplyKeyboardMarkup:
        """
        Returns keyboard for final state

        Args:
            language (str): user's language
        Returns:
            ReplyKeyboardMarkup
        """
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(MessageToUser.translate('Расписание на сегодня  ▶️', language))],
            [KeyboardButton(MessageToUser.translate('Расписание на завтра  ⏩', language))],
            [KeyboardButton(MessageToUser.translate('Расписание на неделю  ⏭', language))],
            [KeyboardButton(MessageToUser.translate('Вернуться назад  ↩️', language))]
        ], resize_keyboard=True)
        return kb
