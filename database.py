'''Database module for Schedule Telegram bot'''


import sqlite3 as sq
from aiogram.dispatcher import FSMContext


class Database:
    '''
    Database class
    '''
    async def db_connect(self) -> None:
        '''Method to connect to database'''
        self.db = sq.connect('users.db')
        self.cur = self.db.cursor()

        self.cur.execute('CREATE TABLE IF NOT EXISTS students(username TEXT PRIMARY KEY, number_group TEXT, state TEXT)')
        self.db.commit()

    async def add_user(self, username: str) -> None:
        '''
        Method to add a new user

        Args:
            username (str): username 
        Returns:
            None
        '''
        user = self.cur.execute('SELECT username FROM students WHERE username=="{}"'.format(username)).fetchone()
        if not user:
            self.cur.execute('INSERT INTO students VALUES(?, ?, ?)', (username, '', 'processing'))
            self.db.commit()

    async def edit_user_group(self, state: FSMContext, username: str) -> None:
        '''
        Method to edit user's group

        Args:
            state (FSMContext): user's state
            username (str): username
        Returns:
            None
        '''
        async with state.proxy() as data:
            self.cur.execute('UPDATE students SET number_group="{}" WHERE username=="{}"'.format(data['group'], username))
            self.db.commit()

    async def edit_user_state(self, state: FSMContext, username: str) -> None:
        '''
        Method to edit user's state

        Args:
            state (FSMContext): user's state
            username (str): username
        Returns:
            None
        '''
        async with state.proxy() as data:
            self.cur.execute('UPDATE students SET state="{}" WHERE username=="{}"'.format(data['state'], username))
            self.db.commit()

    async def get_user_state(self, username: str) -> str:
        '''
        Method to get user's state

        Args:
            username (str): username
        Returns:
            str
        '''
        state = self.cur.execute('SELECT state FROM students WHERE username=="{}"'.format(username)).fetchone()
        if not state:
            return 'processing'
        return state[0]

    async def get_user_group(self, username: str) -> str:
        '''
        Method to get user's group

        Args:
            username (str): username
        Returns:
            str
        '''
        state = self.cur.execute('SELECT number_group FROM students WHERE username=="{}"'.format(username)).fetchone()
        if not state:
            return 'none'
        return state[0]
