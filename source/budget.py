from source.database import Database
from datetime import datetime
from decimal import Decimal

class BudgetManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()

    def set_budget(self, category, amount, month=None, year=None):
        try:
            category = category.strip()
            if not category:
                raise ValueError("Category cannot be empty.")
            
            amount = Decimal(str(amount)).quantize(Decimal('0.00'))
            if amount <= Decimal('0'):
                raise ValueError("Amount must be positive.")
            
            month = month if month is not None else datetime.now().month
            year = year if year is not None else datetime.now().year

            if not 1 <= month <=12:
                raise ValueError("Month must be between 1 and 12.")

            with self.db._get_cursor() as cursor:
                exists = cursor.execute('''SELECT 1 from budget WHERE 
                                        user_id = ? AND category = ? 
                                        AND month = ? AND year = ?''', 
                                        (self.user_id, category, month, year)).fetchone()
                
                if exists:
                    cursor.execute('''UPDATE budget SET amount = ? 
                                    WHERE user_id = ? AND category = ? 
                                    AND month = ? AND year = ?''', 
                                    (str(amount), self.user_id, category, month, year))
                    print(f"Updated budget for {category} ({month}/{year}).")

                else:
                    cursor.execute('''INSERT INTO budget 
                                    (user_id, category, amount, month, year) 
                                    VALUES (?, ?, ?, ?, ?)''', 
                                    (self.user_id, category, str(amount), month, year))
                    print(f"Created new budget for {category} ({month}/{year}).")
                
            print("Budget set successfully.")
            return True
        
        except ValueError as error:
            print(f"Validation error: {str(error)}.")
            return False
        except Exception as error:
            print(f"Database error: {str(error)}.")
            return False
        

    
    def check_budgets(self, month=None, year=None):
        try:
            month = month or datetime.now().month
            year = year or datetime.now().year

            alerts = []
            budgets = self.get_budgets(month, year)

            if not budgets:
                return ["No budgets set for this period."]

            any_exceeded = False
            any_warnings = False

            for budget in budgets:
                category = budget['category']
                spent = abs(Decimal(str(self.get_category_spending(category, month, year))))
                budget_amount = Decimal(str(budget['amount']))
                remaining = budget_amount - spent

                if spent > budget_amount:
                    alerts.append(
                        f"{category}: EXCEEDED by ${(spent - budget_amount):.2f} "
                        f"(Budget: ${budget_amount:.2f}, Spent: ${spent:.2f})"
                    )
                    any_exceeded = True
                elif spent > Decimal('0.8') * budget_amount:
                    alerts.append(
                        f"{category}: WARNING - Nearing limit. "
                        f"(${remaining:.2f} remaining)"
                    )
                    any_warnings = True
                else:
                    alerts.append(
                        f"{category}: Within budget. "
                        f"(${remaining:.2f} remaining)"
                    )

            if not any_exceeded and not any_warnings:
                alerts.append("All budgets are within limits!")
            
            return alerts

        except Exception as error:
            return [f"ERROR: Budget check failed - {str(error)}"]
            

    def get_budgets(self, month, year):
        with self.db._get_cursor() as cursor:
            results = cursor.execute('''
                SELECT category, amount 
                FROM budget
                WHERE user_id = ? AND month = ? AND year = ?
                ''',
                (self.user_id, month, year)
            ).fetchall()

            return [{
                'category': row[0],
                'amount': Decimal(str(row[1]))
            } for row in results]

    def get_category_spending(self, category, month, year):
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-31"

        with self.db._get_cursor() as cursor:
            result = cursor.execute('''
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions 
                WHERE user_id = ? 
                AND type = 'expense'
                AND category = ? 
                AND date BETWEEN ? AND ?
                ''',
                (self.user_id, category, start_date, end_date)
            ).fetchone()
            
            return Decimal(str(result[0]))  # Ensure Decimal return type