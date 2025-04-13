import sys
from datetime import datetime
from decimal import Decimal
from colorama import Fore, Style, init
from tabulate import tabulate
from source.auth import AuthManager
from source.transactions import TransactionManager
from source.reports import ReportGenerator
from source.budget import BudgetManager
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
        

    def show_budget_alerts(self, alerts):
        if not alerts:
            print(f"{Fore.GREEN} All budgets are within limits! {Style.RESET_ALL}")
            return
        
        self.print_header("BUDGET ALERTS")
        for alert in alerts:
            if "exceeded" in alert.lower():
                print(f"{Fore.RED}❌ {alert}{Style.RESET_ALL}")
            elif "warning" in alert.lower():
                print(f"{Fore.YELLOW}⚠️ {alert}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}ℹ️ {alert}{Style.RESET_ALL}")

    
    def main_menu(self):
        self.clear_screen()
        print(f"\n{Fore.CYAN} ================================= {Style.RESET_ALL}")
        print(f"{Fore.YELLOW} PERSONAL FINANCE MANAGER {Style.RESET_ALL}")
        print(f"\n{Fore.CYAN} ================================= {Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}1.{Style.RESET_ALL} Register")
        print(f"\n{Fore.GREEN}2.{Style.RESET_ALL} Login")
        print(f"\n{Fore.GREEN}3.{Style.RESET_ALL} Exit")


    def user_menu(self):
        self.clear_screen()
        balance = ReportGenerator(self.user_id).get_total()
        balance_color = Fore.GREEN if balance >= 0 else Fore.RED
        print(f"\nWelcome, {Fore.YELLOW}{self.current_user}{Style.RESET_ALL}")
        print(f"Current balance: {balance_color}${abs(balance):.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Add Transaction")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} View/Edit Transaction")
        print(f"{Fore.GREEN}3.{Style.RESET_ALL} Financial Reports")
        print(f"{Fore.GREEN}4.{Style.RESET_ALL} Budget Management")
        print(f"{Fore.GREEN}5.{Style.RESET_ALL} Data tools")
        print(f"{Fore.GREEN}6.{Style.RESET_ALL} Logout")

    def run(self):
        while True:
            self.main_menu()
            choice=self.get_valid_input("Choose an option (1-3): ", int, [1, 2, 3])

            if choice == 1:
                if self.auth.register_user():
                    print(f"{Fore.GREEN}Registration successful![{Style.RESET_ALL}")
            
            elif choice == 2:
                self.current_user = self.auth.login_user()
                if self.current_user:
                    self.user_id=self.db.get_user_id(self.current_user)
                    if self.user_id:
                        self.user_session()
                else:
                    print(f"{Fore.RED}Error: User not found{Style.RESET_ALL}")
            
            elif choice == 3:
                print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                sys.exit()
    
    def user_session(self):
        trans_manager = TransactionManager(self.user_id)
        report_gen = ReportGenerator(self.user_id)
        budget_manager = BudgetManager(self.user_id)

        while True:
            self.user_menu()
            choice = self.get_valid_input("Choose an option (1-6): ", int, range(1, 7))

            if choice == 1:
                self.clear_screen()
                self.print_header("New Transaction")
                trans_type = self.get_valid_input("Type(Income/Expense): ", str, ["income", "expense"])
                category = input("Category: ").strip()
                amount = self.get_valid_input("Amount: $", "decimal")
                description = input("Descriptional(optional): ").strip()

                if trans_manager.add_transaction(trans_type, category, amount, description):
                    print(f"{Fore.GREEN}✓ Transaction recorded!{Style.RESET_ALL}")
                input("\nPress Enter to continue...")

            elif choice == 2:
                self.clear_screen()
                self.print_header("Your Transactions")
                transactions = trans_manager.get_transactions()
                self.show_transactions(transactions)

                input("\nPress Enter to continue...")

            elif choice == 3:
                self.clear_screen()
                self.print_header("Financial Reports")
                print(f"{Fore.GREEN}1.{Style.RESET_ALL} Monthly Report")
                print(f"{Fore.GREEN}2.{Style.RESET_ALL} Yearly Report")
                print(f"{Fore.GREEN}3.{Style.RESET_ALL} Category Breakdown")
                report_choice = self.get_valid_input("Choose report type (1-3): ", int, [1, 2, 3])

                if report_choice == 1:
                    month = self.get_valid_input("Month(1-12): ", int, range(1, 13))
                    year = self.get_valid_input("Year: ", int)
                    report = report_gen.monthly_salary(month, year)
                elif report_choice == 2:
                    year = self.get_valid_input("Year: ", int)
                    report = report_gen.yearly_salary(year)
                else:
                    pass
                self.show_report(report, "month" if report_choice == 1 else "year")
                input("\nPress Enter to continue...")

            elif choice == 4:
                self.clear_screen()
                self.print_header("Budget Tools")
                print(f"{Fore.GREEN}1.{Style.RESET_ALL} Set Budget")
                print(f"{Fore.GREEN}2.{Style.RESET_ALL} Check Budget Status")
                budget_choice = self.get_valid_input("Choose an option (1-2): ", int, [1, 2])

                if budget_choice == 1:
                    category = input("Category: ").strip()
                    amount = self.get_valid_input("Monthly budget: $", "decimal")
                    budget_manager.set_budget(category, amount)
                    print(f"{Fore.GREEN}✓ Budget Set!{Style.RESET_ALL}")
                else:
                    alerts = budget_manager.check_budgets()
                    self.show_budget_alerts(alerts)

                input("\nPress Enter to continue...")

            elif choice == 5:
                self.clear_screen()
                self.print_header("Data Management")
                print(f"{Fore.GREEN}1.{Style.RESET_ALL} Backup Data")
                print(f"{Fore.GREEN}2.{Style.RESET_ALL} Restore Data")
                print(f"{Fore.GREEN}3.{Style.RESET_ALL} Export Transactions")
                data_choice = self.get_valid_input("Choose an option (1-3): ", int, [1, 2, 3])

                if data_choice == 1:
                    self.db.backup_data()
                elif data_choice == 2:
                    self.db.restor_data()
                else:
                    filename = input("Export filename (default: transactions.csv): ").strip() or "transactions.csv"
                    self.db.export_transactions(self.user_id, filename)
                    print(f"{Fore.GREEN}✓ Data exported to {filename}{Style.RESET_ALL}")

                input("\nPress Enter to continue...")

            elif choice == 6:
                self.current_user = None
                self.user_id = None
                break


if __name__ == "__main__":
    app = FinanceManager()
    app.run()







        





