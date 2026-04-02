import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import BOT_TOKEN, GROUP_ID
from database.db import init_db, get_all_completed_users, get_group_id
from handlers import user_handlers, admin_handlers
from utils.excel_exporter import export_users_to_excel

# Setup logging
logging.basicConfig(level=logging.INFO)

async def send_auto_excel(bot: Bot):
    dynamic_group_id = await get_group_id()
    group_to_send = dynamic_group_id if dynamic_group_id else GROUP_ID
    
    if not group_to_send:
        logging.warning("No GROUP_ID specified in .env or DB, cannot send auto excel.")
        return
        
    try:
        users = await get_all_completed_users()
        if not users:
            logging.info("No completed users. Skip sending auto Excel.")
            return

        filepath = export_users_to_excel(users, "kunlik_arizalar.xlsx")
        document = FSInputFile(filepath)
        await bot.send_document(
            chat_id=group_to_send,
            document=document,
            caption="⏰ <b>Avtomatik Excel Hisoboti</b>\n\nJami kelib tushgan arizalar.",
            parse_mode="HTML"
        )
        logging.info("Auto Excel successfully sent to group.")
    except Exception as e:
        logging.error(f"Error sending auto excel: {e}")

async def main():
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_routers(
        admin_handlers.router,
        user_handlers.router
    )
    
    # Scheduler setup
    scheduler = AsyncIOScheduler(timezone='Asia/Tashkent')
    scheduler.add_job(send_auto_excel, CronTrigger(hour=6, minute=0), args=(bot,))
    scheduler.add_job(send_auto_excel, CronTrigger(hour=12, minute=0), args=(bot,))
    scheduler.start()
    
    try:
        logging.info("Bot is starting...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
