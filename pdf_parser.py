import camelot
import json


class Lesson:
    start_time = None
    end_time = None
    pass


class NormalLesson(Lesson):
    CODE = "0"
    disc = None

    def __init__(self, st_time: str, ed_time: str, text: str) -> None:
        self.start_time = st_time
        self.end_time = ed_time
        self.disc = text

    def __str__(self) -> str:
        return f"0 {self.CODE} {self.start_time} {self.end_time} {self.disc}"


class DoubleLesson(Lesson):
    CODE = "1"
    disc_up = None
    disc_down = None

    def __init__(self, st_time: str, ed_time: str, text_up: str, text_down: str) -> None:
        self.start_time = st_time
        self.end_time = ed_time
        self.disc_up = text_up
        self.disc_down = text_down

    def __str__(self) -> str:
        return f"1 {self.CODE} {self.start_time} {self.end_time} {self.disc_up} {self.disc_down}"


class Parser:
    WEEKDAYS = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")

    @staticmethod
    def pdf_to_json(filename_pdf: str, filename_json: str) -> None:
        data = {}
        with open(filename_json, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise json.decoder.JSONDecodeError("Not a dictionary", "", 0)
            except json.decoder.JSONDecodeError:
                data = {}
        print(data)

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
        data = None

        with open(filename_json, "r") as f:
            data = json.load(f)

        for grn in data:
            print(f"GROUP {grn}")
            for day in data[grn]:
                print(f"{grn} DAY {day}")
                print(*data[grn][day], sep="\n")

    @staticmethod
    def get_lesson_from_json(filename_json: str, group_number: str) -> dict:
        with open(filename_json, "r") as f:
            data = json.load(f)
            return data[group_number]
