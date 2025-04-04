from datetime import datetime
from database import Database
from decimal import Decimal

class TransactionManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()


    def add_transaction(self, trans_type, category, amount, description=""):   
        try:
            trans_type = trans_type.lower()
            if trans_type not in ('income', 'expense'):
                raise ValueError("Type must be 'income' or 'expense'")
            
            amount = Decimal(str(amount))
            if amount <= Decimal('0'):
                raise ValueError("Amount must be positive")

            db_amount = amount if trans_type == 'income' else -amount
                                                                     
            date = datetime.now().date().isoformat()
            with self.db._get_cursor() as cursor:
                cursor.execute('''INSERT INTO transactions 
                            (user_id, type, category, amount, date, description)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (self.user_id, trans_type, category.strip(), 
                             str(db_amount), date, description.strip()))
            print("Transaction added successfully!")

        except ValueError as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Database error: {e}")
            return False


    def get_transactions(self, start_date = None, end_date = None):
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [self.user_id]

        if start_date and end_date:
            query += "AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        with self.db._get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


    def delete_transaction(self, trans_id):
        with self.db._get_cursor() as cursor:
            cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", 
                           (trans_id, self.user_id))
            
            if cursor.rowcount > 0:
                print("Transaction deleted!")
            
            else:
                print("No transaction found with that ID.")


    def get_balance(self):
        with self.db._get_cursor() as cursor:
            cursor.execute('''SELECT 
                           SUM (CASE WHEN type = 'income' THEN amount ELSE -amount END) 
                           FROM transactions WHERE user_id = ?''', 
                           (self.user_id))
            balance = cursor.fetchone()[0]
            return Decimal(balance) if balance is not None else Decimal('0')
        
