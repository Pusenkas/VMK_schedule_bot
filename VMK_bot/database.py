"""Database module for Schedule Telegram bot."""

import sqlite3 as sq
from aiogram.dispatcher import FSMContext


class Database:
    """Singleton database class."""

    def __new__(cls):
        """Method new."""
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def connect(self) -> None:
        """Method to connect to database."""
        if not hasattr(self, 'db'):
            self.db = sq.connect('users.db')
            self.cur = self.db.cursor()

        self.cur.execute(
            'CREATE TABLE IF NOT EXISTS students(username TEXT PRIMARY KEY, group_number TEXT, state TEXT)')
        self.db.commit()
        self.cur.execute(
            'CREATE TABLE IF NOT EXISTS schedule(group_number TEXT, parity BOOL, Понедельник TEXT, Вторник TEXT,'
            'Среда TEXT, Четверг TEXT, Пятница TEXT, Суббота TEXT)')
        self.db.commit()
        self.cur.execute('CREATE TABLE IF NOT EXISTS hashes(hash TEXT)')
        self.db.commit()

    def update_schedule(self, group_number: str, parity: bool, table_entry: list[str]) -> None:
        """Method to update table schedule with new entry.

        Args:
            group_number (str): user's group
            parity (bool): parity of the week
            table_entry (list[str]): list of schedules for each day in a week
        """
        self.cur.execute('INSERT INTO schedule VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                         (group_number, parity, *table_entry))
        self.db.commit()

    def get_valid_groups(self) -> list[str]:
        """Method to get valid groups.

        Returns:
            list[str]
        """
        groups = self.cur.execute('SELECT DISTINCT group_number FROM schedule').fetchall()
        return [group[0] for group in groups]

    def get_schedule(self, group_number: str, parity: bool, weekday: str) -> str:
        """Method to get schedule by group_number, parity of week and weekday.

        Args:
            group_number (str): user's group
            parity (bool): parity of the week
            weekday (str): day of the week
        Returns:
            str
        """
        schedule = self.cur.execute('SELECT {} FROM schedule WHERE group_number=="{}" AND parity=={}'
                                    .format(weekday, group_number, parity)).fetchone()
        return schedule[0]

    def add_user(self, username: str) -> None:
        """Method to add a new user.

        Args:
            username (str): username
        """
        user = self.cur.execute('SELECT username FROM students WHERE username=="{}"'.format(username)).fetchone()
        if not user:
            self.cur.execute('INSERT INTO students VALUES(?, ?, ?)', (username, '', 'processing'))
            self.db.commit()

    async def edit_user_group(self, state: FSMContext, username: str) -> None:
        """Method to edit user's group.

        Args:
            state (FSMContext): user's state
            username (str): username
        """
        async with state.proxy() as data:
            self.cur.execute(
                'UPDATE students SET group_number="{}" WHERE username=="{}"'.format(data['group'], username))
            self.db.commit()

    async def edit_user_state(self, state: FSMContext, username: str) -> None:
        """Method to edit user's state.

        Args:
            state (FSMContext): user's state
            username (str): username
        """
        async with state.proxy() as data:
            self.cur.execute('UPDATE students SET state="{}" WHERE username=="{}"'.format(data['state'], username))
            self.db.commit()

    def get_user_state(self, username: str) -> str:
        """Method to get user's state.

        Args:
            username (str): username
        Returns:
            str
        """
        state = self.cur.execute('SELECT state FROM students WHERE username=="{}"'.format(username)).fetchone()
        if not state:
            return 'processing'
        return state[0]

    def get_user_group(self, username: str) -> str:
        """Method to get user's group.

        Args:
            username (str): username
        Returns:
            str
        """
        state = self.cur.execute('SELECT group_number FROM students WHERE username=="{}"'.format(username)).fetchone()
        if not state:
            return 'none'
        return state[0]

    def add_hash(self, my_hash: str) -> bool:
        """Method to add a new hash.

        Args:
            my_hash (str): hash to store in database

        Returns:
            bool: True if my_hash is in database. Otherwise False

        """
        user = self.cur.execute('SELECT hash FROM hashes WHERE hash=="{}"'.format(my_hash)).fetchone()
        if not user:
            self.cur.execute('INSERT INTO hashes VALUES(?)', (my_hash,))
            self.db.commit()
            return False
        return True
