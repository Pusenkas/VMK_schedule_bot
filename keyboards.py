'''Keyboards module for Schedule Telegram bot'''


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class Keyboards:
    '''
    Class of keyboards for user
    '''
    @staticmethod
    def get_start_kb() -> ReplyKeyboardMarkup:
        '''
        Returns initial keyboard

        Returns:
            ReplyKeyboardMarkup
        '''
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('/help'),
             KeyboardButton('/schedule')]
        ], resize_keyboard=True)
        return kb

    @staticmethod
    def get_schedule_option_kb() -> ReplyKeyboardMarkup:
        '''
        Returns option keyboard for option_processing state

        Returns:
            ReplyKeyboardMarkup
        '''
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('/today_schedule'),
             KeyboardButton('/week_schedule')]
        ], resize_keyboard=True)
        return kb

    @staticmethod
    def get_cancel_kb() -> ReplyKeyboardMarkup:
        '''
        Returns keyboard for final state

        Returns:
            ReplyKeyboardMarkup
        '''
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton('/return_to_menu'),
             KeyboardButton('/change_group_number')]
        ], resize_keyboard=True)
        return kb
