from datetime import datetime
from source.database import Database
from decimal import Decimal

class ReportGenerator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()

    def monthly_salary(self, month, year):
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"
        
        with self.db._get_cursor() as c:
            c.execute('''SELECT COALESCE(SUM(amount), 0) 
                    FROM transactions 
                    WHERE user_id=? AND amount > 0
                    AND date BETWEEN ? AND ?''',
                    (self.user_id, start_date, end_date))
            income = float(c.fetchone()[0])
            
            c.execute('''SELECT COALESCE(SUM(amount), 0) 
                    FROM transactions 
                    WHERE user_id=? AND amount < 0
                    AND date BETWEEN ? AND ?''',
                    (self.user_id, start_date, end_date))
            expenses = abs(float(c.fetchone()[0]))
            
            balance = income - expenses
            savings_rate = (balance / income * 100) if income > 0 else 0
            
        return {
            'income': income,
            'expenses': expenses,
            'balance': balance,
            'savings_rate': savings_rate,
            'month': month,
            'year': year
        }

    def yearly_salary(self, year):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        with self.db._get_cursor() as c:
            c.execute('''SELECT COALESCE(SUM(amount), 0) 
                    FROM transactions 
                    WHERE user_id=? AND amount > 0
                    AND date BETWEEN ? AND ?''',
                    (self.user_id, start_date, end_date))
            income = float(c.fetchone()[0])
            
            c.execute('''SELECT COALESCE(SUM(amount), 0) 
                    FROM transactions 
                    WHERE user_id=? AND amount < 0
                    AND date BETWEEN ? AND ?''',
                    (self.user_id, start_date, end_date))
            expenses = abs(float(c.fetchone()[0]))
            
            balance = income - expenses
            savings_rate = (balance / income * 100) if income > 0 else 0
            
            c.execute('''SELECT strftime('%m', date) as month,
                        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                        ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) as expenses
                        FROM transactions 
                        WHERE user_id=? AND date BETWEEN ? AND ?
                        GROUP BY month''',
                    (self.user_id, start_date, end_date))
            monthly_data = c.fetchall()
            
        return {
            'income': income,
            'expenses': expenses,
            'balance': balance,
            'savings_rate': savings_rate,
            'year': year,
            'monthly_breakdown': monthly_data
        }
    
    def category_breakdown(self, month=None, year=None):
        date_filter = ""
        params = [self.user_id]
        
        if month and year:
            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-31"
            date_filter = "AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        elif year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            date_filter = "AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        with self.db._get_cursor() as cursor:
            cursor.execute(f'''SELECT category, SUM(amount) as total
                    FROM transactions
                    WHERE user_id=? AND amount > 0 {date_filter}
                    GROUP BY category''', params)
            income_by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute(f'''SELECT category, ABS(SUM(amount)) as total
                    FROM transactions
                    WHERE user_id=? AND amount < 0 {date_filter}
                    GROUP BY category''', params)
            expenses_by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
        return {
            'income': income_by_category,
            'expenses': expenses_by_category,
            'month': month,
            'year': year
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
                        FROM transactions 
                        WHERE user_id=?''',
                        (self.user_id,))  
            total = cursor.fetchone()[0]
            return float(total) if total is not None else 0.0
        



