import aiosqlite

DB_NAME = "database/database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
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
        await db.commit()

async def get_user(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def start_user(telegram_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (telegram_id, username, status) 
            VALUES (?, ?, 'started') 
            ON CONFLICT(telegram_id) DO UPDATE SET status='started'
        """, (telegram_id, username))
        await db.commit()

async def save_user_data(telegram_id, data: dict):
    # Converts a dictionary to a database update query
    fields = [
        "ism", "familiya", "otasining_ismi", "telefon", "email",
        "manzil_viloyat", "manzil_tuman", "manzil_mahalla", "manzil_kocha", "manzil_uy",
        "pasport_raqam", "pasport_fayl", "tugilgan_sana", "diplom_fayl",
        "yonalish", "talim_shakli", "sertifikat_fayl"
    ]
    query_parts = []
    values = []
    for field in fields:
        if field in data:
            query_parts.append(f"{field} = ?")
            values.append(data[field])
    
    if not query_parts:
        return
        
    query_parts.append("status = ?")
    values.append("completed")
    
    values.append(telegram_id)
    
    query = f"UPDATE users SET {', '.join(query_parts)} WHERE telegram_id = ?"
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query, tuple(values))
        await db.commit()

async def reset_user(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE status='started'") as c:
            started = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE status='completed'") as c:
            completed = (await c.fetchone())[0]
        return {"total": total, "started": started, "completed": completed}

async def get_all_completed_users():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE status='completed'") as cursor:
            return await cursor.fetchall()

async def get_all_started_users():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE status='started'") as cursor:
            return await cursor.fetchall()

async def get_all_users_for_message():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT telegram_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
