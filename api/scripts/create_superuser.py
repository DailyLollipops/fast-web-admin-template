# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "bcrypt",
#     "pydantic-settings",
#     "pymysql",
#     "redis",
#     "sqlmodel",
# ]
# ///
import re
from getpass import getpass

import bcrypt
from database import get_sync_db
from database.models.user import User


def is_valid_email(email: str) -> bool:
    """Basic email format validation using regex."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return re.match(pattern, email) is not None


def main():
    title = """
######################################
#                                    #
#     Superuser Account Creation     #
#                                    #
######################################
"""
    print(title)
    name = input('Enter name: ')
    while True:
        email = input('Enter email: ').strip()
        if is_valid_email(email):
            break
        print('❌  Invalid email format. Please try again.')

    password = None
    while True:
        pw1 = getpass('Enter password: ')
        pw2 = getpass('Confirm password: ')
        
        if pw1 == pw2:
            password = pw1
            break
    
        print('❌  Passwords do not match.')
        choice = input('Try again? (y/n): ').strip().lower()
        if choice != 'y':
            print('⚠️  Account creation aborted.')
            return

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role='system',
        verified=True,
    )

    db = next(get_sync_db())
    db.add(user)
    db.commit()

    print('✅  Account created successfully!')


if __name__ == '__main__':
    main()
