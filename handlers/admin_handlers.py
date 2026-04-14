from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, ADMIN_ID
from keyboards.inline import admin_menu, arizalar_list_keyboard, back_to_admin_keyboard, xabar_turi_keyboard, user_detail_keyboard, settings_menu, admins_list_keyboard
from states.forms import AdminMessage, AdminSettings
from database.db import get_stats, get_all_completed_users, get_user, get_all_users_for_message, get_all_started_users, reset_user, get_all_admins, add_admin, remove_admin, get_group_id, set_group_id, get_user_by_db_id, delete_user_by_db_id
from utils.excel_exporter import export_users_to_excel
from utils.archive import create_user_archive

import os

class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        admins = await get_all_admins()
        return event.from_user.id in admins

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    text = "🧑‍💻 <b>Admin Panelga xush kelibsiz!</b>\n\nQuyidagi menyudan kerakli bo'limni tanlang 👇"
    await message.answer(text, parse_mode="HTML", reply_markup=admin_menu())

@router.callback_query(F.data == "admin_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🧑‍💻 <b>Admin Panelga xush kelibsiz!</b>\n\nQuyidagi menyudan kerakli bo'limni tanlang 👇"
    
    # Agar xabarda hujjat yoki rasm bo'lsa, 'edit_text' xato beradi (Telegram API cheklovi)
    if callback.message.document or callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_menu())
    else:
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_menu())
        except Exception:
            # Har qanday kutilmagan xatoda (masalan, matn o'zgarmagan bo'lsa)
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_menu())

@router.callback_query(F.data == "admin_stats")
async def process_stats(callback: CallbackQuery):
    stats = await get_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami userlar: <b>{stats['total']}</b>\n"
        f"🟡 Jarayonda qolganlar: <b>{stats['started']}</b>\n"
        f"🟢 Tugatganlar: <b>{stats['completed']}</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_admin_keyboard())

@router.callback_query(F.data == "admin_arizalar")
async def process_arizalar(callback: CallbackQuery):
    users = await get_all_completed_users()
    if not users:
        await callback.message.edit_text("🚫 Hali arizalar yo'q.", reply_markup=back_to_admin_keyboard())
        return
        
    await callback.message.edit_text("📂 <b>Arizalar ro'yxati:</b>", parse_mode="HTML", reply_markup=arizalar_list_keyboard(users))

@router.callback_query(F.data == "admin_qolganlar")
async def process_qolganlar(callback: CallbackQuery):
    users = await get_all_started_users()
    if not users:
        await callback.message.edit_text("🚫 Hali jarayonda qolganlar yo'q.", reply_markup=back_to_admin_keyboard())
        return
        
    await callback.message.edit_text("🟡 <b>Jarayonda qolganlar ro'yxati:</b>", parse_mode="HTML", reply_markup=arizalar_list_keyboard(users))

@router.callback_query(F.data.startswith("user_"))
async def process_user_detail(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    user = await get_user(user_id)
    
    if not user:
        await callback.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return
        
    text = (
        "👤 <b>Foydalanuvchi ma'lumoti</b>\n\n"
        f"<b>Ismi:</b> {user['ism']}\n"
        f"<b>Familiyasi:</b> {user['familiya']}\n"
        f"<b>Otasi:</b> {user['otasining_ismi']}\n"
        f"<b>Tel:</b> {user['telefon']}\n"
        f"<b>Email:</b> {user['email']}\n"
        f"<b>Manzil:</b> {user['manzil_viloyat']}, {user['manzil_tuman']}\n"
        f"<b>Pasport:</b> {user['pasport_raqam']}\n"
        f"<b>Tug'ilgan sana:</b> {user['tugilgan_sana']}\n"
        f"<b>Yo'nalish:</b> {user['yonalish']}\n"
        f"<b>Telegram ID:</b> <code>{user['telegram_id']}</code>"
    )
    
    # Create and send zip if completed and has files
    if user['status'] == 'completed':
        zip_path = create_user_archive(user)
        if os.path.exists(zip_path):
            document = FSInputFile(zip_path)
            await callback.message.answer_document(document, caption=text, parse_mode="HTML", reply_markup=user_detail_keyboard(user['telegram_id']))
        else:
            await callback.message.answer(text, parse_mode="HTML", reply_markup=user_detail_keyboard(user['telegram_id']))
    else:
        text += "\n\n⚠️ <i>Foydalanuvchi ariza to'ldirishni to'liq yakunlamagan!</i>"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=user_detail_keyboard(user['telegram_id']))

@router.callback_query(F.data.startswith("msguser_"))
async def process_msg_specific_user(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    await state.update_data(user_id=user_id)
    await callback.message.answer(f"✍️ <code>{user_id}</code> ga yubormoqchi bo'lgan xabaringizni kiriting:", parse_mode="HTML")
    await state.set_state(AdminMessage.bittaga_xabar)

@router.callback_query(F.data.startswith("deluser_"))
async def process_del_specific_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await reset_user(user_id)
    await callback.answer("✅ Foydalanuvchi o'chirildi!", show_alert=True)
    await cmd_admin(callback.message)

@router.callback_query(F.data == "admin_excel")
async def process_excel(callback: CallbackQuery):
    users = await get_all_completed_users()
    if not users:
        await callback.message.edit_text("🚫 Ma'lumot yo'q.", reply_markup=back_to_admin_keyboard())
        return
        
    filepath = export_users_to_excel(users)
    doc = FSInputFile(filepath)
    await callback.message.delete()
    await callback.message.answer_document(doc, caption="📥 <b>Barcha arizalar excel ko'rinishida</b>", parse_mode="HTML")
    # Restore menu
    await cmd_admin(callback.message)

@router.callback_query(F.data == "admin_xabar")
async def process_xabar_menu(callback: CallbackQuery):
    await callback.message.edit_text("📨 Xabar yuborish turini tanlang:", reply_markup=xabar_turi_keyboard())

@router.callback_query(F.data == "xabar_barchaga")
async def xabar_barchaga(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✍️ Barcha userlarga yuboriladigan xabarni kiriting:\n\n<i>Bekor qilish uchun /cancel yozing.</i>", parse_mode="HTML")
    await state.set_state(AdminMessage.barchaga)

@router.message(Command("cancel"))
async def cancel_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Harakat bekor qilindi.")

@router.message(AdminMessage.barchaga)
async def process_barchaga_xabar(message: Message, state: FSMContext, bot: Bot):
    text = message.text or message.caption or "..."
    users = await get_all_users_for_message()
    sent = 0
    for uid in users:
        try:
            await bot.send_message(chat_id=uid, text=text, parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ Xabar jami <b>{sent}</b> userga yetkazildi.", parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data == "xabar_bittaga")
async def xabar_bittaga(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("👤 User ID ni kiriting:", parse_mode="HTML")
    await state.set_state(AdminMessage.bittaga_id)

@router.message(AdminMessage.bittaga_id)
async def process_bittaga_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ User ID faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    await state.update_data(user_id=int(message.text))
    await message.answer("✍️ Xabar matnini kiriting:", parse_mode="HTML")
    await state.set_state(AdminMessage.bittaga_xabar)

@router.message(AdminMessage.bittaga_xabar)
async def process_bittaga_xabar(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("user_id")
    text = message.text or message.caption
    
    try:
        await bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
        await message.answer("✅ Xabar muvaffaqiyatli yetkazildi.")
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xatolik yuz berdi: {e}")
        
    await state.clear()

@router.callback_query(F.data == "admin_settings")
async def process_settings_menu(callback: CallbackQuery):
    await callback.message.edit_text("⚙️ <b>Sozlamalar paneli</b>\n\nNimani sozlamoqchisiz?", reply_markup=settings_menu(), parse_mode="HTML")

@router.callback_query(F.data == "settings_group")
async def process_settings_group(callback: CallbackQuery, state: FSMContext):
    current_group = await get_group_id()
    text = f"👥 <b>Guruh ID</b>\n\nHozirgi ulangan guruh: <code>{current_group or 'Ulangan emas'}</code>\n\nYangi guruh ID ni kiriting (yoki /cancel yozing):"
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(AdminSettings.set_group_id)

@router.message(AdminSettings.set_group_id)
async def handle_set_group_id(message: Message, state: FSMContext):
    await set_group_id(message.text)
    await message.answer(f"✅ Guruh ID muvaffaqiyatli saqlandi: <code>{message.text}</code>\n\nYangi arizalar ushbu guruhga tushadi.", parse_mode="HTML")
    await state.clear()
    
@router.callback_query(F.data == "settings_admins")
async def process_settings_admins(callback: CallbackQuery):
    admins = await get_all_admins()
    await callback.message.edit_text("👨‍💻 <b>Adminlar ro'yxati</b>", parse_mode="HTML", reply_markup=admins_list_keyboard(admins))

@router.callback_query(F.data == "add_admin")
async def add_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("➕ Yangi adminning Telegram ID raqamini kiriting:", parse_mode="HTML")
    await state.set_state(AdminSettings.add_admin)

@router.message(AdminSettings.add_admin)
async def process_add_admin(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Noto'g'ri ID. Raqam kiriting:")
        return
    await add_admin(int(message.text))
    await message.answer(f"✅ Admin qo'shildi: <code>{message.text}</code>", parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data == "remove_admin")
async def remove_admin_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("➖ O'chirmoqchi bo'lgan adminning Telegram ID sini yozing:", parse_mode="HTML")
    await state.set_state(AdminSettings.remove_admin)

@router.message(AdminSettings.remove_admin)
async def process_remove_admin(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Noto'g'ri ID. Raqam kiriting:")
        return
    admin_id = int(message.text)
    from config import ADMIN_IDS
    if admin_id in ADMIN_IDS:
        await message.answer("⚠️ .env faylidagi asosiy adminlarni o'chirib bo'lmaydi!")
    else:
        await remove_admin(admin_id)
        await message.answer(f"✅ Admin o'chirildi: <code>{message.text}</code>", parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data == "admin_delete_user_prompt")
async def process_admin_delete_user_prompt(callback: CallbackQuery, state: FSMContext):
    text = "🗑 <b>O'chirmoqchi bo'lgan foydalanuvchining DB ID raqamini kiriting:</b>\n\n<i>(DB ID raqam Excel faylining eng chapida joylashgan bo'ladi)</i>"
    from keyboards.inline import back_to_admin_keyboard
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_admin_keyboard())
    await state.set_state(AdminSettings.delete_user_id)

@router.message(AdminSettings.delete_user_id)
async def process_delete_user_input(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Noto'g'ri ID. Faqat raqam kiriting:")
        return
        
    db_id = int(message.text)
    user = await get_user_by_db_id(db_id)
    
    if not user:
        await message.answer(f"🚫 DB ID <b>{db_id}</b> bo'lgan foydalanuvchi topilmadi. Qaytadan kiriting:", parse_mode="HTML")
        return
        
    name = f"{user['ism'] or ''} {user['familiya'] or ''}".strip()
    if not name:
        name = "Kiritilmagan"
        
    text = (
        "⚠️ <b>Quyidagi foydalanuvchini bazadan butunlay o'chirib tashlamoqchimisiz?</b>\n\n"
        f"<b>DB ID:</b> {user['id']}\n"
        f"<b>Ism Familiya:</b> {name}\n"
        f"<b>Telefon:</b> {user['telefon'] or 'Yoq'}\n"
        f"<b>Telegram ID:</b> {user['telegram_id']}"
    )
    from keyboards.inline import confirm_delete_user_keyboard
    await message.answer(text, parse_mode="HTML", reply_markup=confirm_delete_user_keyboard(user['id']))
    await state.clear()

@router.callback_query(F.data.startswith("confirmdel_"))
async def process_confirm_deluser(callback: CallbackQuery):
    db_id = int(callback.data.split("_")[1])
    await delete_user_by_db_id(db_id)
    await callback.message.edit_text(f"✅ DB ID <b>{db_id}</b> bo'lgan foydalanuvchi bazadan to'liq o'chirildi!", parse_mode="HTML")
    await cmd_admin(callback.message)
