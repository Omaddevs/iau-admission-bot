import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bir nechta admin ID larni vergul bilan ajratib yozish mumkin
# Misol: ADMIN_IDS=123456,789012,345678
_admin_ids_raw = os.getenv("ADMIN_IDS", os.getenv("ADMIN_ID", "0"))
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip().isdigit()]
ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else 0  # Birinchi admin - asosiy (primary) admin

GROUP_ID = int(os.getenv("GROUP_ID", 0))

# PostgreSQL sozlamalari
DB_NAME = os.getenv("DB_NAME", "iau_admission_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Make sure folders exist
os.makedirs("media/photos", exist_ok=True)
os.makedirs("media/documents", exist_ok=True)
os.makedirs("media/archives", exist_ok=True)
os.makedirs("media/exports", exist_ok=True)
