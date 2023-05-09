"""User Interface module"""
import gettext


class MessageToUser:
    """
    Performs translation of message into user's language - en/ru
    """
    @staticmethod
    def _translate_into_language(message: str, _) -> str:
        """
        Private method that helps gettext to find patterns to translate

        Args:
            message (str): message to user
        Returns:
            str
        """
        POSSIBLE_MESSAGES = {
            'Вы превысили лимит сообщений. Подождите': _('Вы превысили лимит сообщений. Подождите'),
            'Добро пожаловать!\nЯ бот, отправляющий расписание ВМК': _('Добро пожаловать!\nЯ бот, отправляющий расписание ВМК'),
            'Для получения расписания введите номер вашей учебной группы': _('Для получения расписания введите номер вашей учебной группы'),
            '/start - начать работу с ботом\n/help - получить подсказки по командам': _('/start - начать работу с ботом\n/help - получить подсказки по командам'),
            'Держите ваше расписание на сегодня\n': _('Держите ваше расписание на сегодня\n'),
            'Держите ваше расписание на неделю\n': _('Держите ваше расписание на неделю\n'),
            'Держите ваше расписание на завтра\n': _('Держите ваше расписание на завтра\n'),
            'Вы вернулись в главное меню': _('Вы вернулись в главное меню'),
            'Выберите опцию!': _('Выберите опцию!'),
            'Неверный номер группы!\nПовторите попытку': _('Неверный номер группы!\nПовторите попытку'),
            'Расписание на сегодня  ▶️': _('Расписание на сегодня  ▶️'),
            'Расписание на завтра  ⏩': _('Расписание на завтра  ⏩'),
            'Расписание на неделю  ⏭': _('Расписание на неделю  ⏭'),
            'Вернуться назад  ↩️': _('Вернуться назад  ↩️')
        }

        return POSSIBLE_MESSAGES[message]

    @staticmethod
    def translate(message: str, language: str) -> str:
        """
        Translates message into user's language

        Args:
            message (str): message to user
            language (str): user's language
        Returns:
            str
        """
        translation = gettext.translation('user', 'VMK_bot/translation', languages=[language], fallback=True)
        _ = translation.gettext

        return MessageToUser._translate_into_language(message, _)
