import sys
import hashlib
from source.database import Database

class AuthManager:
    def __init__(self):
        self.db = Database()
    
    def _get_password(self, prompt="Password: "):
        password = []
        try:
            if sys.platform == 'win32':
                import msvcrt
                print(prompt, end='', flush=True)
                while True:
                    ch = msvcrt.getch().decode('utf-8')
                    if ch == '\r':  # Enter
                        print()
                        break
                    elif ch == '\b':  # Backspace
                        if password:
                            password.pop()
                            print('\b \b', end='', flush=True)
                    else:
                        password.append(ch)
                        print('*', end='', flush=True)
            
            else:
                import tty, termios
                print(prompt, end='', flush=True)
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    while True:
                        ch = sys.stdin.read(1)
                        if ch in ('\r', '\n'):
                            print()
                            break
                        elif ch == '\x7f':  # Backspace
                            if password:
                                password.pop()
                                sys.stdout.write('\b \b')
                        else:
                            password.append(ch)
                            sys.stdout.write('*')
                        sys.stdout.flush()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            # Fallback to regular getpass if something fails
            import getpass
            return getpass.getpass(prompt)
        return ''.join(password)

    def register_user(self):
        username = input("Enter username: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            return False
            
        if self.db.user_exists(username):
            print("Error: Username already exists!")
            return False
        
        password = self._get_password("Enter password: ")
        if not password:
            print("Error: Password cannot be empty")
            return False
            
        confirm = self._get_password("Confirm password: ")
        if password != confirm:
            print("Error: Passwords don't match!")
            return False

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        self.db.add_user(username, hashed_pw)
        print("\nRegistration successful!")
        return True
    
    def login_user(self):
        username = input("Enter username: ").strip()
        if not username:
            print("Error: Username required")
            return None
            
        password = self._get_password("Enter password: ")
        if not password:
            print("Error: Password required")
            return None

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if self.db.verify_user(username, hashed_pw):
            print("\nLogin successful!")
            return username
        else:
            print("\nError: Invalid credentials!")
            return None

        

