import os

import asyncpg
import asyncio
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
POSTGRES_URL = os.getenv("POSTGRES_URL")


async def create_table():
    conn = await asyncpg.connect(POSTGRES_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    await conn.close()


asyncio.run(create_table())


# username был unique возможно в рабочей бд все еще юник
async def create_users_table():
    conn = await asyncpg.connect(POSTGRES_URL)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
    finally:
        await conn.close()


asyncio.run(create_users_table())
