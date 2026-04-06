import os
from dotenv import load_dotenv

load_dotenv()

print('Current environment variables:')
print(f'DB_HOST: {os.getenv("DB_HOST")}')
print(f'DB_PORT: {os.getenv("DB_PORT")}')
print(f'DB_USER: {os.getenv("DB_USER")}')
print(f'DB_PASSWORD: {"***" + os.getenv("DB_PASSWORD")[-4:] if os.getenv("DB_PASSWORD") else "None"}')
print(f'DB_NAME: {os.getenv("DB_NAME")}')
print(f'FLASK_ENV: {os.getenv("FLASK_ENV")}')