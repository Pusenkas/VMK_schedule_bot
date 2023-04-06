import sqlite3 as sq
from aiogram.dispatcher import FSMContext


async def db_connect() -> None:
    global db, cur

    db = sq.connect('users.db')
    cur = db.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS students(username TEXT PRIMARY KEY, number_group TEXT, state TEXT)')
    db.commit()


async def add_user(username: str) -> None:
    user = cur.execute('SELECT username FROM students WHERE username=="{}"'.format(username)).fetchone()
    if not user:
        cur.execute('INSERT INTO students VALUES(?, ?, ?)', (username, '', 'processing'))
        db.commit()


async def edit_user_group(state: FSMContext, username: str) -> None:
    async with state.proxy() as data:
        cur.execute('UPDATE students SET number_group="{}" WHERE username=="{}"'.format(data['group'], username))
        db.commit()


async def edit_user_state(state: FSMContext, username: str) -> None:
    async with state.proxy() as data:
        cur.execute('UPDATE students SET state="{}" WHERE username=="{}"'.format(data['state'], username))
        db.commit()


async def get_user_state(username: str) -> str:
    state = cur.execute('SELECT state FROM students WHERE username=="{}"'.format(username)).fetchone()
    if not state:
        return 'processing'
    return state[0]


async def get_user_group(username: str) -> str:
    state = cur.execute('SELECT number_group FROM students WHERE username=="{}"'.format(username)).fetchone()
    if not state:
        return 'none'
    return state[0]
