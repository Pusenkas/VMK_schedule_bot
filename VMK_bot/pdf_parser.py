"""Module for parsing pdf tables and saving data into database."""

import camelot
import shlex
from VMK_bot.database import Database
import json
from datetime import datetime


class Lesson:
    """Lesson class to be inherited.

    Args:
        start_time (str): Class start time
        end_time (str): Class finish time
    """

    start_time = None
    end_time = None


class NormalLesson(Lesson):
    """Normal lesson.

    Args:
        description (str): text that describes normal lesson
    """

    CODE = "0"
    description = None

    def __init__(self, start_time: str, end_time: str, description: str) -> None:
        """Init method."""
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

    def __str__(self) -> str:
        """Str method."""
        return f"{self.CODE} {self.start_time} {self.end_time} '{self.description}'"


class DoubleLesson(Lesson):
    """Odd/even week lesson.

    Args:
        description_up (str): description for a odd week lesson
        description_down (str): description for a even week lesson
    """

    CODE = "1"
    description_up = None
    description_down = None

    def __init__(self, start_time: str, end_time: str, description_up: str, description_down: str) -> None:
        """Init method."""
        self.start_time = start_time
        self.end_time = end_time
        self.description_up = description_up
        self.description_down = description_down

    def __str__(self) -> str:
        """Str method."""
        return f"{self.CODE} {self.start_time} {self.end_time} '{self.description_up}' '{self.description_down}'"


class Parser:
    """PDF table parser, which can transform it into database."""

    WEEKDAYS = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")

    @staticmethod
    def number_to_weekday(number: int) -> str:
        """Returns string repr of weekday by its number.

        Args:
            number (int): number of weekday
        Returns:
            str
        """
        if number == 6:
            return 'Воскресенье'
        return Parser.WEEKDAYS[number]

    @staticmethod
    def parse_schedule(filename_pdf: str) -> dict:
        """Static method that extract data from pdf table.

        Args:
            filename_pdf (str): name of pdf table file
        Returns:
            dict: Data from parsed schedule
        """
        data = {}

        # extracting tables from pdf
        tables = camelot.read_pdf(filename_pdf, line_scale=110, copy_text=['v', 'h'], pages='all')
        for page in tables:
            df = page.df
            if df[0][0] not in Parser.WEEKDAYS:
                df = df.iloc[1:, :]
                df.index = range(len(df))
            if df.iloc[0, -1] in Parser.WEEKDAYS:  # removing double dates
                df = df.iloc[:, :-1]
            i, group_number_filled = 0, False
            current_weekday, groups = None, None
            while i < df.shape[0]:
                match df[0][i].split("-"):
                    case [week_day] if week_day in Parser.WEEKDAYS:
                        if not group_number_filled:
                            data |= {group_number:
                                     {day: [] for day in Parser.WEEKDAYS} for group_number in df.loc[i, 1:]}
                            groups = [group_number for group_number in df.loc[i, 1:]]
                            group_number_filled = True
                        current_weekday = week_day
                    case [start_time, end_time]:
                        if i + 1 < df.shape[0] and df[0][i] == df[0][i + 1]:
                            for group_number, lesson_up, lesson_down in zip(groups, df.loc[i, 1:], df.loc[i + 1, 1:]):
                                if lesson_up == lesson_down:
                                    data[group_number][current_weekday].append(
                                        str(NormalLesson(start_time, end_time, lesson_up)))
                                else:
                                    data[group_number][current_weekday].append(
                                        str(DoubleLesson(start_time, end_time, lesson_up, lesson_down)))
                            i += 1
                        else:
                            for group_number, lesson in zip(groups, df.loc[i, 1:]):
                                data[group_number][current_weekday].append(
                                    str(NormalLesson(start_time, end_time, lesson)))
                    case _:
                        pass
                i += 1

        return data

    @staticmethod
    def import_schedule_to_database(filename_pdf: str) -> None:
        """Static method that imports given pdf table into database.

        Args:
            filename_pdf (str): name of pdf table file
        """
        data = Parser.parse_schedule(filename_pdf)

        # import schedule into database
        db = Database()
        db.connect()

        valid_characters = set("0123456789/")  # valid characters in group number
        for group_number in data.keys():
            if set(group_number) <= valid_characters:
                for parity in [False, True]:
                    table_entry = list()
                    for weekday in Parser.WEEKDAYS:
                        table_entry.append(Parser.get_schedule_day(data, group_number, parity, weekday))
                    db.update_schedule(group_number, parity, table_entry)

    @staticmethod
    def mark_day_schedule(day_schedule: list[str], tomorrow: bool) -> list[str]:
        """Marks lessons as passed (red), in progress (yellow) and will be (green).

        Args:
            day_schedule (list[str]): list of all lessons for the day
            tomorrow (bool): True if this request not for today and shouldn't be marked
        Returns:
            list[str]
        """
        MARKS = {'after': '🔴', 'during': '🟡', 'before': '🟢'}

        marked = list()
        for i, lesson in enumerate(day_schedule, 1):
            _, start_time, end_time, description = shlex.split(lesson)

            mark = ''
            if not tomorrow:
                start_hour, start_minute = map(int, start_time.split('.'))
                end_hour, end_minute = map(int, end_time.split('.'))

                now = datetime.now()
                start = now.replace(hour=start_hour, minute=start_minute, second=0)
                end = now.replace(hour=end_hour, minute=end_minute, second=0)

                mark = MARKS['during'] if start <= now <= end else MARKS['before'] if now < start else MARKS['after']

            if description:
                marked.append(Parser._pretty_lesson_str(i, start_time, end_time, description) + ' ' + mark)

        return marked

    @staticmethod
    def get_today_schedule(group_number: str, parity: bool, weekday: str) -> str:
        """Returns today's schedule for user.

        Args:
            group_number (str): user's group
            parity (bool): parity of the week
            weekday (str): day of the week
        Returns:
            str
        """
        if weekday == 'Воскресенье':
            return 'Не волнуйтесь, это воскресенье 🥳'

        db = Database()
        db.connect()

        today_schedule = db.get_schedule(group_number, parity, weekday)
        tomorrow = Parser.number_to_weekday(datetime.today().weekday()) != weekday  # True if this request not for today
        today_schedule = Parser.mark_day_schedule(json.loads(today_schedule), tomorrow=tomorrow)

        return '\n'.join([f'<b>{weekday}</b>'] + today_schedule)

    @staticmethod
    def get_week_schedule(group_number: str, parity: bool) -> str:
        """Returns week's schedule for user.

        Args:
            group_number (str): user's group
            parity (bool): parity of the week
        Returns:
            str
        """
        db = Database()
        db.connect()

        week_schedule = ''
        for weekday in Parser.WEEKDAYS:
            schedule_list = db.get_schedule(group_number, parity, weekday)
            schedule_list = json.loads(schedule_list)

            day_schedule = f'<b>{weekday}</b>\n'
            for i, lesson in enumerate(schedule_list, 1):
                _, start_time, end_time, description = shlex.split(lesson)
                if description:
                    day_schedule += Parser._pretty_lesson_str(i, start_time, end_time, description) + '\n'

            week_schedule += day_schedule

        return week_schedule

    @staticmethod
    def get_schedule_day(data: dict['str', 'str'], group_number: str, odd_week: bool, day: str) -> str:
        """Return schedule of chosen group on day in json format.

        Args:
            data: schedule data
            group_number (str): group number
            odd_week (bool): is current week odd or even?
            day (str): day of the week
        Returns:
            str: schedule on day
        """
        data = data[group_number][day]

        res = list()
        for i, lesson in enumerate(data, 1):
            match shlex.split(lesson):
                case [NormalLesson.CODE, start_time, end_time, description]:
                    res.append(str(NormalLesson(start_time, end_time, description)))
                case [DoubleLesson.CODE, start_time, end_time, _, description] if odd_week:
                    res.append(str(NormalLesson(start_time, end_time, description)))
                case [DoubleLesson.CODE, start_time, end_time, description, _] if not odd_week:
                    res.append(str(NormalLesson(start_time, end_time, description)))
                case _:
                    pass

        return json.dumps(res)

    @staticmethod
    def _pretty_lesson_str(i: int, start_time: str, end_time: str, description: str):
        """Used for string formatting."""
        if description:
            description = " ".join(description.replace('\n', ' ').split())
            return f"{i}) ({start_time}-{end_time}) {description}"
        return ""
