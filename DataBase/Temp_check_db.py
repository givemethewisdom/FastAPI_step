import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def quick_check():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    # 1. Таблицы
    print("=" * 60)
    print("ТАБЛИЦЫ:")
    tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    for t in tables:
        print(f"  • {t['table_name']}")

    # 2. Количество записей
    print("\nКОЛИЧЕСТВО ЗАПИСЕЙ:")
    for t in tables:
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {t['table_name']}")
        print(f"  • {t['table_name']}: {count} записей")

    # 3. Структура первой таблицы
    if tables:
        print(f"\nСТРУКТУРА ТАБЛИЦЫ '{tables[0]['table_name']}':")
        cols = await conn.fetch(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='{tables[0]['table_name']}'
        """)
        for c in cols:
            print(f"  • {c['column_name']}: {c['data_type']}")

    await conn.close()

