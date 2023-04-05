"""
"""

import camelot
import json
import shlex


class Lesson:
    """Lesson class to be inherited

    Args:
        start_time (str): Class start time
        end_time (str): Class finish time
    """
    start_time = None
    end_time = None


class NormalLesson(Lesson):
    """Normal lesson

    Args:
        description (str): text that describes normal lesson
    """

    CODE = "0"
    description = None

    def __init__(self, start_time: str, end_time: str, description: str) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

    def __str__(self) -> str:
        return f"{self.CODE} {self.start_time} {self.end_time} '{self.description}'"


class DoubleLesson(Lesson):
    """Odd/even week lesson

    Args:
        description_up (str): description for a odd week lesson
        description_down (str): description for a even week lesson
    """
    CODE = "1"
    description_up = None
    description_down = None

    def __init__(self, start_time: str, end_time: str, description_up: str, description_down: str) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.description_up = description_up
        self.description_down = description_down

    def __str__(self) -> str:
        return f"{self.CODE} {self.start_time} {self.end_time} '{self.description_up}' '{self.description_down}'"


class Parser:
    """PDF table parser, which can transform it into the json data"""
    WEEKDAYS = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")

    @staticmethod
    def pdf_to_json(filename_pdf: str, filename_json: str) -> None:
        """Static method that transform given pdf table into json and store it into the file

        Args:
            filename_pdf (str): name of pdf table file
            filename_json (str): name of json file to store data in json format
        Returns:
            None
        """
        data = {}
        with open(filename_json, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise json.decoder.JSONDecodeError("Not a dictionary", "", 0)
            except json.decoder.JSONDecodeError:
                data = {}

        tables = camelot.read_pdf(filename_pdf, line_scale=80, copy_text=['v', 'h'], pages='all')
        for page in tables:
            df = page.df
            if df.iloc[0, -1] in Parser.WEEKDAYS:  # removing double dates
                df = df.iloc[:, :-1]

            i, group_number_filled = 0, False
            current_weekday, groups = None, None
            while i < df.shape[0]:
                match df[0][i].split():
                    case [week_day] if week_day in Parser.WEEKDAYS:
                        if not group_number_filled:
                            data |= {group_number:
                                         {day: [] for day in Parser.WEEKDAYS} for group_number in df.loc[i, 1:]}
                            groups = [group_number for group_number in df.loc[i, 1:]]
                            group_number_filled = True
                        current_weekday = week_day
                    case [start_time, "-", end_time]:
                        if i + 1 < df.shape[0] and df[0][i] == df[0][i + 1]:
                            for group_number, lesson_up, lesson_down in zip(groups, df.loc[i, 1:], df.loc[i + 1, 1:]):
                                if lesson_up == lesson_down:
                                    data[group_number][current_weekday].append(
                                        NormalLesson(start_time, end_time, lesson_up))
                                else:
                                    data[group_number][current_weekday].append(
                                        DoubleLesson(start_time, end_time, lesson_up, lesson_down))
                        else:
                            for group_number, lesson in zip(groups, df.loc[i, 1:]):
                                data[group_number][current_weekday].append(NormalLesson(start_time, end_time, lesson))
                    case _:
                        pass
                i += 1
        with open(filename_json, "w") as f:
            json.dump(data, f, default=lambda x: str(x))

    @staticmethod
    def pretty_print_json(filename_json: str) -> None:
        """Method for pretty printing json file

        Args:
            filename_json (str): name of json file
        Returns:
            None
        """
        data = None

        with open(filename_json, "r") as f:
            data = json.load(f)

        for grn in data:
            print(f"GROUP {grn}")
            for day in data[grn]:
                print(f"{grn} DAY {day}")
                print(*data[grn][day], sep="\n")

    @staticmethod
    def get_schedule_week(filename_json: str, group_number: str, odd_week: bool) -> str:
        """Return schedule of chosen group on week

        Args:
            filename_json (str): name of json file with schedule data
            group_number (str): group number
            odd_week (bool): is current week odd or even?
        Returns:
            str: schedule on day in pretty text format
        """
        with open(filename_json, "r") as f:
            data = json.load(f)[group_number]
            res = ""
            for weekday in data:
                res += weekday + "\n"
                res += Parser.get_schedule_day(filename_json, group_number, odd_week, weekday)
            return res

    @staticmethod
    def get_schedule_day(filename_json: str, group_number: str, odd_week: bool, day: str) -> str:
        """Return schedule of chosen group on  day

        Args:
            filename_json (str): name of json file with schedule data
            group_number (str): group number
            odd_week (bool): is current week odd or even?
            day (str): day of the week
        Returns:
            str: schedule on day in pretty text format
        """
        with open(filename_json, "r") as f:
            data = json.load(f)[group_number][day]
            res = ""
            for i, lesson in enumerate(data, 1):
                match shlex.split(lesson):
                    case [NormalLesson.CODE, start_time, end_time, description]:
                        res += Parser._pretty_lesson_str(i, start_time, end_time, description)
                    case [DoubleLesson.CODE, start_time, end_time, _, description] if odd_week:
                        res += Parser._pretty_lesson_str(i, start_time, end_time, description)
                    case [DoubleLesson.CODE, start_time, end_time, description, _] if not odd_week:
                        res += Parser._pretty_lesson_str(i, start_time, end_time, description)
                    case _:
                        pass
            return res

    @staticmethod
    def _pretty_lesson_str(i: int, start_time: str, end_time: str, description: str):
        """Used for string formatting"""
        if description:
            description = " ".join(description.replace('\n', ' ').split())
            return f"{i}) ({start_time}-{end_time}) {description}\n"
        return ""
