import getpass
import hashlib
from database import Database

class AuthManager:
    def __init__(self):
        self.db = Database()


    def register_user(self):
        username = input("Enter username: ")
        if self.db.user_exists(username):
            print("Username already exists!")
            return False
        
        password = getpass.getpass("Enter password: ")
        hashed_pw= hashlib.sha256(password.encode()).hexdigest()

        self.db.add_user(username, hashed_pw)
        print("Registration successful!")
        return True
    
    
    def login_user(self):
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        if self.db.verify_user(username, hashed_pw):
            print("Login successful!")
            return username
        else:
            print("Invalid credentials!")
            return None
        

        

