import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self):
        self._init_db()

    @contextmanager
    def _get_cursor(self):
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._get_cursor() as cursor:
            #User Table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           username TEXT UNIQUE, 
                           password TEXT)''')
            
            #Transaction Table
            cursor.execute('''CREATE TABLE IF NOT EXISTS transaction
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_id INTEGER, 
                           type TEXT,
                           # 'income' or 'expense' category TEXT,
                           amount REAL, 
                           date DATE, 
                           description TEXT, 
                           FORIEGN KEY(user_id) REFERENCES users (id))''')
            
            #Budget Table
            cursor.execute('''CREATE TABLE IF NOT EXISTS budget
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_id INTEGER, category TEXT, 
                           amount REAL, 
                           month INTEGER, 
                           year INTEGER, 
                           FOREIGN KEY(user_id) REFERENCES users(id))''')
            
            def user_exists(self, username):
                with self._get_cursor() as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE username=?", (username))
                    return cursor.fetchone() is not None
                
            def add_user(self, username, password):
                with self._get_cursor() as cursor:
                    cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))

            def verify_users(self, username, password):
                with self._get_cursor() as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE username=? AND password=?", (username, password))
                    return cursor.fetchone() is not None


