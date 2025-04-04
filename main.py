import sys
from datetime import datetime
from decimal import Decimal
from colorama import Fore, Style, init
from tabulate import tabulate
from source.auth import AuthManager
from source.transactions import TransactionManager
from source.reports import ReportGenerator
from database import Database

init()

class FinanceManager():
    def __init__(self):
        self.auth = AuthManager()
        self.db = Database()
        self.current_user = None
        self.user_id = None

    def clear_screen(self):
        print("\033c", end="")

    def print_header(self, title):
        print(f"\n{Fore.CYAN} === {title} === {Style.RESET_ALL}")

    def get_valid_input(self, prompt, input_type=str, valid_options=None):
        while True:
            try:
                user_input = input(prompt)
                if input_type == int:
                    user_input = int(user_input)
                elif input_type == float:
                    user_input = float(user_input)
                elif input_type == "decimal":
                    user_input = Decimal(user_input)

                if valid_options and user_input not in valid_options:
                    raise ValueError
                
                return user_input
            
            except ValueError:
                print(f"{Fore.RED}Invalid input! Please try again.{Style.RESET_ALL}")

    def show_transactions(self, transactions):
        if not transactions:
            print (f"{Fore.YELLOW}No transactions found.{Style.RESET_ALL}")
            return
        
        headers = ["ID", "Type", "Category", "Amount", "Date", "Description"]
        table_data=[]
        for t in transactions:
            color = Fore.GREEN if t[2] == 'income' else Fore.RED
            amount_color = Fore.GREEN if float(t[4]) >= 0 else Fore.RED

            table_data.append([t[0], 
                               color + t[2] + Style.RESET_ALL, 
                               t[3], amount_color + f"${float(t[4]):.2f}" + Style.RESET_ALL, 
                               t[5], 
                               t[6]])
            
        print(tabulate(table_data, headers=headers, tablefmt="grid"))


    def show_report(self, report, period_type):
        self.print_header(f"{period_type.capitalize()} Report")

        if period_type == "month":
            print(f"Period: {report['month']}/{report['year']}")
        else:
            print(f"Period: {report['year']}")

        table_data = [
            [f"{Fore.GREEN}Income{Style.RESET_ALL}", f"${report['income']:.2f}"],
            [f"{Fore.RED}Expenses{Style.RESET_ALL}", f"${report['expenses']:.2f}"],
            [f"{Fore.BLUE}Net Balance{Style.RESET_ALL}", f"${report['balance']:.2f}"]
        ]

        print(tabulate(table_data, tablefmt="fancy_grid"))


