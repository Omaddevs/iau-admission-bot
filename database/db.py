import asyncpg
import logging
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

pool = None

async def init_db():
    global pool
    # Ma'lumotlar bazasini yaratishga harakat qilinadi (agar yo'q bo'lsa)
    # Buning uchun default 'postgres' bazasiga ulanamiz
    try:
        sys_conn = await asyncpg.connect(
            user=DB_USER, 
            password=DB_PASSWORD, 
            database='postgres', 
            host=DB_HOST, 
            port=DB_PORT
        )
        exists = await sys_conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME)
        if not exists:
            # CREATE DATABASE transaction ichida ishlamaydi, shuning uchun alohida bajaramiz
            await sys_conn.execute(f'CREATE DATABASE "{DB_NAME}"')
        await sys_conn.close()
    except Exception as e:
        logging.error(f"Error creating db (maybe already exists or no permission): {e}")

    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

    async with pool.acquire() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                ism TEXT,
                familiya TEXT,
                otasining_ismi TEXT,
                telefon TEXT,
                email TEXT,
                manzil_viloyat TEXT,
                manzil_tuman TEXT,
                manzil_mahalla TEXT,
                manzil_kocha TEXT,
                manzil_uy TEXT,
                pasport_raqam TEXT,
                pasport_fayl TEXT,
                tugilgan_sana TEXT,
                diplom_fayl TEXT,
                yonalish TEXT,
                talim_shakli TEXT,
                sertifikat_fayl TEXT,
                status TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                telegram_id BIGINT PRIMARY KEY
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

async def get_all_admins():
    from config import ADMIN_IDS
    admins = list(ADMIN_IDS)
    try:
        if pool:
            async with pool.acquire() as db:
                rows = await db.fetch("SELECT telegram_id FROM admins")
                admins.extend([row['telegram_id'] for row in rows])
    except Exception as e:
        logging.error(f"Error getting admins: {e}")
    return list(set(admins))

async def add_admin(telegram_id):
    async with pool.acquire() as db:
        await db.execute("INSERT INTO admins (telegram_id) VALUES ($1) ON CONFLICT DO NOTHING", telegram_id)

async def remove_admin(telegram_id):
    async with pool.acquire() as db:
        await db.execute("DELETE FROM admins WHERE telegram_id = $1", telegram_id)

async def get_group_id():
    async with pool.acquire() as db:
        row = await db.fetchrow("SELECT value FROM settings WHERE key = 'group_id'")
        return row['value'] if row else None

async def set_group_id(group_id):
    async with pool.acquire() as db:
        await db.execute("""
            INSERT INTO settings (key, value) VALUES ('group_id', $1) 
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, str(group_id))

async def get_user(telegram_id):
    async with pool.acquire() as db:
        row = await db.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        return dict(row) if row else None

async def get_user_by_db_id(user_db_id):
    async with pool.acquire() as db:
        row = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_db_id)
        return dict(row) if row else None

async def start_user(telegram_id, username):
    async with pool.acquire() as db:
        await db.execute("""
            INSERT INTO users (telegram_id, username, status) 
            VALUES ($1, $2, 'started') 
            ON CONFLICT(telegram_id) DO UPDATE SET status='started'
        """, telegram_id, username)

async def save_user_data(telegram_id, data: dict, status=None):
    fields = [
        "ism", "familiya", "otasining_ismi", "telefon", "email",
        "manzil_viloyat", "manzil_tuman", "manzil_mahalla", "manzil_kocha", "manzil_uy",
        "pasport_raqam", "pasport_fayl", "tugilgan_sana", "diplom_fayl",
        "yonalish", "talim_shakli", "sertifikat_fayl"
    ]
    query_parts = []
    values = []
    idx = 1
    for field in fields:
        if field in data:
            query_parts.append(f"{field} = ${idx}")
            values.append(data[field])
            idx += 1
    
    if status is not None:
        query_parts.append(f"status = ${idx}")
        values.append(status)
        idx += 1
        
    if not query_parts:
        return
        
    values.append(telegram_id)
    
    query = f"UPDATE users SET {', '.join(query_parts)} WHERE telegram_id = ${idx}"
    async with pool.acquire() as db:
        await db.execute(query, *values)

async def reset_user(telegram_id):
    async with pool.acquire() as db:
        await db.execute("DELETE FROM users WHERE telegram_id = $1", telegram_id)

async def delete_user_by_db_id(user_db_id):
    async with pool.acquire() as db:
        await db.execute("DELETE FROM users WHERE id = $1", user_db_id)

async def get_stats():
    async with pool.acquire() as db:
        total = await db.fetchval("SELECT COUNT(*) FROM users")
        started = await db.fetchval("SELECT COUNT(*) FROM users WHERE status='started'")
        completed = await db.fetchval("SELECT COUNT(*) FROM users WHERE status='completed'")
        return {"total": total or 0, "started": started or 0, "completed": completed or 0}

async def get_all_completed_users():
    async with pool.acquire() as db:
        rows = await db.fetch("SELECT * FROM users WHERE status='completed'")
        return [dict(row) for row in rows]

async def get_all_started_users():
    async with pool.acquire() as db:
        rows = await db.fetch("SELECT * FROM users WHERE status='started'")
        return [dict(row) for row in rows]

async def get_all_users_for_message():
    async with pool.acquire() as db:
        rows = await db.fetch("SELECT telegram_id FROM users")
        return [row['telegram_id'] for row in rows]
