from datetime import datetime
from database import Database
from decimal import Decimal

class ReportGenerator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()


    def monthly_salary(self, month, year):
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"

        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? AND amount > 0 
                           AND date BETWEEN ? and ?''', 
                           (self.user_id, start_date, end_date))
            income = float(cursor.fetchone()[0])   

            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? AND amount < 0 
                           AND date BETWEEN ? and ?''', 
                           (self.user_id, start_date, end_date)) 
            expenses = float(cursor.fetchone()[0])   
   
        return{
            'income' : income,
            'expenses' : abs(expenses),
            'savings' : income + expenses,
            'month' : month,
            'year' : year,
        }
    
    
    def yearly_salary(self, year):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? AND amount > 0 
                           AND date BETWEEN ? and ?''', 
                           (self.user_id, start_date, end_date))
            income = float(cursor.fetchone()[0])   

            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? AND amount < 0 
                           AND date BETWEEN ? and ?''', 
                           (self.user_id, start_date, end_date)) 
            expenses = float(cursor.fetchone()[0])   
   
        return{
            'income' : income,
            'expenses' : abs(expenses),
            'savings' : income + expenses,
            'year' : year,
        }
    

    def get_positive_total(self, start_date, end_date):
        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? AND amount > 0 
                           AND date BETWEEN ? and ?''', 
                           (self.user_id, start_date, end_date))
            return Decimal(cursor.fetchone()[0])   
        

    def get_negative_total(self, start_date, end_date):
        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? AND amount < 0 
                           AND date BETWEEN ? and ?''', 
                           (self.user_id, start_date, end_date))
            return Decimal(cursor.fetchone()[0])   
        

    def get_total(self):
        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT COALESCE(SUM(amount), 0)
                           FROM transactions WHERE user_id = ? ''', 
                           (self.user_id))
            total = cursor.fetchone()[0]
            return float(total) if total is not None else 0.0
           

        



