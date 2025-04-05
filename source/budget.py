from database import Database
from datetime import datetime

class BudgetManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()

    def set_budget(self, category, amount, month=None, year=None):
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT id from budget WHERE 
                           user_id = ? AND category = ? 
                           AND month = ? AND year = ?''', 
                           (self.user_id, category, month, year))
            
            if cursor.fetchone():
                cursor.execute()