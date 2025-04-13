from contextlib import contextmanager
import sqlite3

class Database:
    def __init__(self, db_path='finance.db'):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_cursor(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._get_cursor() as cursor:
            # Users table
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           username TEXT UNIQUE, 
                           password TEXT)''')
            
            # Transactions table
            cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_id INTEGER, 
                           type TEXT CHECK(type IN ('income', 'expense')),
                           category TEXT,
                           amount DECIMAL(10,2) NOT NULL, 
                           date TEXT NOT NULL, 
                           description TEXT, 
                           FOREIGN KEY(user_id) REFERENCES users(id))''')
            
            # Budget table
            cursor.execute('''CREATE TABLE IF NOT EXISTS budget
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_id INTEGER, 
                           category TEXT NOT NULL,
                           amount DECIMAL(10,2) NOT NULL,
                           month INTEGER CHECK(month BETWEEN 1 AND 12),
                           year INTEGER NOT NULL,
                           FOREIGN KEY(user_id) REFERENCES users(id),
                           UNIQUE(user_id, category, month, year))''')

    def user_exists(self, username):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
            return cursor.fetchone() is not None

    def add_user(self, username, password):
        with self._get_cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         (username, password))

    def verify_user(self, username, password):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username=? AND password=?", 
                         (username, password))
            return cursor.fetchone() is not None
        
    def get_user_id(self, username):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        
    def backup_data(self, backup_file='finance.db'):
        import shutil
        shutil.copy2('finance.db', backup_file)
        print(f"Backup created at {backup_file}")

    def restore_data(self, backup_file='finance.db'):
        import shutil
        shutil.copy2(backup_file, 'finance.db')
        print("Data restored from backup.")

    def export_transactions(self, user_id, filename='transactions.csv'):
        import csv
        with self._get_cursor() as cursor:
            cursor.execute('''SELECT type, category, amount, date, description 
                           FROM transactions WHERE user_id=?''', (user_id,))
            transactions = cursor.fetchall()

            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Type', 'Category', 'Amount', 'Date', 'Description'])
                writer.writerows(transactions)

            print(f"Transactions exported to {filename}")




