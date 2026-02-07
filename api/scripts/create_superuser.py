# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiomysql",
#     "argon2-cffi",
#     "passlib",
#     "pydantic-settings",
#     "pymysql",
#     "redis",
#     "sqlmodel",
# ]
# ///
import re
from getpass import getpass

from passlib.context import CryptContext

from api.database import get_sync_session
from api.database.models.user import User


pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

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

    user = User(
        name=name,
        email=email,
        password=pwd_context.hash(password),
        role='system',
        provider='native',
        verified=True,
    )

    with get_sync_session() as session:
        session.add(user)
        session.commit()

    print('✅  Account created successfully!')


if __name__ == '__main__':
    main()
