from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.forms import AdmissionForm
from keyboards.reply import phone_keyboard, remove_keyboard
from keyboards.inline import yonalish_keyboard, tasdiqlash_keyboard, language_keyboard, regions_keyboard, districts_keyboard
from database.db import start_user, save_user_data, reset_user
from utils.texts import TEXTS
from utils.mapping import YONALISH_MAP
from config import ADMIN_ID
import os
import re

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await start_user(message.from_user.id, message.from_user.username)
    text = (
        "🇺🇿 Iltimos, tilni tanlang:\n\n"
        "🇷🇺 Пожалуйста, выберите язык:\n\n"
        "🇬🇧 Please choose language:"
    )
    await message.answer(text, reply_markup=language_keyboard())
    await state.set_state(AdmissionForm.language)

@router.callback_query(AdmissionForm.language, F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.edit_text(TEXTS[lang]["welcome"], parse_mode="HTML")
    await callback.message.answer(TEXTS[lang]["ask_first_name"], parse_mode="HTML")
    await state.set_state(AdmissionForm.ism)

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "❓ <b>Yordam kerakmi?</b>\n\n"
        "Admin bilan bog‘laning: @iau-support-admin"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(AdmissionForm.ism, F.text)
async def process_ism(message: Message, state: FSMContext):
    await state.update_data(ism=message.text)
    data = await state.get_data()
    lang = data.get("language", "uz")
    await message.answer(TEXTS[lang]["ask_last_name"], parse_mode="HTML")
    await state.set_state(AdmissionForm.familiya)

@router.message(AdmissionForm.familiya, F.text)
async def process_familiya(message: Message, state: FSMContext):
    await state.update_data(familiya=message.text)
    data = await state.get_data()
    lang = data.get("language", "uz")
    await message.answer(TEXTS[lang]["ask_father_name"], parse_mode="HTML")
    await state.set_state(AdmissionForm.otasining_ismi)

@router.message(AdmissionForm.otasining_ismi, F.text)
async def process_otasi(message: Message, state: FSMContext):
    await state.update_data(otasining_ismi=message.text)
    data = await state.get_data()
    lang = data.get("language", "uz")
    await message.answer(TEXTS[lang]["ask_phone"], 
                         parse_mode="HTML", reply_markup=phone_keyboard(lang))
    await state.set_state(AdmissionForm.telefon)

@router.message(AdmissionForm.telefon)
async def process_telefon(message: Message, state: FSMContext):
    if message.contact:
        tel = message.contact.phone_number
    else:
        tel = message.text
    await state.update_data(telefon=tel)
    data = await state.get_data()
    lang = data.get("language", "uz")
    await message.answer(TEXTS[lang]["ask_email"], 
                         parse_mode="HTML", reply_markup=remove_keyboard())
    await state.set_state(AdmissionForm.email)

@router.message(AdmissionForm.email, F.text)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "uz")
    if "@" not in message.text or "." not in message.text:
        await message.answer(TEXTS[lang]["invalid_email"])
        return
    await state.update_data(email=message.text)
    await message.answer(TEXTS[lang]["ask_region"], parse_mode="HTML", reply_markup=regions_keyboard())
    await state.set_state(AdmissionForm.manzil_viloyat)

@router.callback_query(AdmissionForm.manzil_viloyat, F.data.startswith("region_"))
async def process_viloyat(callback: CallbackQuery, state: FSMContext):
    region_name = callback.data.replace("region_", "")
    await state.update_data(manzil_viloyat=region_name)
    data = await state.get_data()
    lang = data.get("language", "uz")
    await callback.message.edit_text(f"✅ {region_name}")
    await callback.message.answer(TEXTS[lang]["ask_district"], parse_mode="HTML", reply_markup=districts_keyboard(region_name))
    await state.set_state(AdmissionForm.manzil_tuman)

@router.callback_query(AdmissionForm.manzil_tuman, F.data.startswith("district_"))
async def process_tuman(callback: CallbackQuery, state: FSMContext):
    district_name = callback.data.replace("district_", "")
    await state.update_data(manzil_tuman=district_name)
    data = await state.get_data()
    lang = data.get("language", "uz")
    await callback.message.edit_text(f"✅ {district_name}")
    await callback.message.answer(TEXTS[lang]["ask_passport"], parse_mode="HTML")
    await state.set_state(AdmissionForm.pasport_raqam)

@router.message(AdmissionForm.pasport_raqam, F.text)
async def process_pasport_raqam(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "uz")
    if not re.match(r"^[A-Za-z0-9]{7,14}$", message.text):
        await message.answer(TEXTS[lang]["invalid_passport"])
        return
    await state.update_data(pasport_raqam=message.text.upper())
    await message.answer(TEXTS[lang]["ask_birth_date"], parse_mode="HTML")
    await state.set_state(AdmissionForm.tugilgan_sana)

@router.message(AdmissionForm.tugilgan_sana, F.text)
async def process_tugilgan_sana(message: Message, state: FSMContext):
    await state.update_data(tugilgan_sana=message.text)
    data = await state.get_data()
    lang = data.get("language", "uz")
    from keyboards.inline import yonalish_keyboard
    await message.answer(TEXTS[lang]["ask_direction"], parse_mode="HTML", reply_markup=yonalish_keyboard())
    await state.set_state(AdmissionForm.yonalish)

@router.callback_query(AdmissionForm.yonalish, F.data.startswith("yonalish_"))
async def process_yonalish(callback: CallbackQuery, state: FSMContext):
    yonalish_code = callback.data.replace("yonalish_", "")
    display_yonalish = YONALISH_MAP.get(yonalish_code, yonalish_code)
    await state.update_data(yonalish=display_yonalish)
    await callback.message.edit_text(f"✅ {display_yonalish}")
    
    data = await state.get_data()
    lang = data.get("language", "uz")
    
    if "MSc" in display_yonalish:
        from keyboards.inline import msc_shakl_keyboard
        await callback.message.answer(TEXTS[lang]["ask_msc_type"], parse_mode="HTML", reply_markup=msc_shakl_keyboard(lang))
        await state.set_state(AdmissionForm.msc_shakl)
    else:
        await callback.message.answer(TEXTS[lang]["ask_passport_file"], parse_mode="HTML")
        await state.set_state(AdmissionForm.pasport_fayl)

@router.callback_query(AdmissionForm.msc_shakl, F.data.startswith("msc_"))
async def process_msc_shakl(callback: CallbackQuery, state: FSMContext):
    msc_type = callback.data.replace("msc_", "").replace("_", " ") # "Full time" or "Part time"
    data = await state.get_data()
    lang = data.get("language", "uz")
    
    # Append to yonalish text
    current_yonalish = data.get("yonalish", "")
    new_yonalish = f"{current_yonalish} ({msc_type})"
    await state.update_data(yonalish=new_yonalish)
    
    await callback.message.edit_text(f"✅ {msc_type}")
    
    # Now go to file uploads
    await callback.message.answer(TEXTS[lang]["ask_passport_file"], parse_mode="HTML")
    await state.set_state(AdmissionForm.pasport_fayl)

@router.message(AdmissionForm.pasport_fayl, F.photo | F.document)
async def process_pasport_fayl(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "uz")
    bot = message.bot
    if message.photo:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = f"media/photos/{file_id}.jpg"
        await bot.download_file(file.file_path, file_path)
    elif message.document:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        if message.document.file_size > 20 * 1024 * 1024:
            await message.answer(TEXTS[lang]["file_too_large"])
            return
        file_name = message.document.file_name
        file_path = f"media/documents/{file_id}_{file_name}"
        await bot.download_file(file.file_path, file_path)
    
    await state.update_data(pasport_fayl=file_path)
    await message.answer(TEXTS[lang]["ask_diplom_file"], parse_mode="HTML")
    await state.set_state(AdmissionForm.diplom_fayl)

@router.message(AdmissionForm.diplom_fayl, F.photo | F.document)
async def process_diplom_fayl(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "uz")
    bot = message.bot
    if message.photo:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = f"media/photos/{file_id}.jpg"
        await bot.download_file(file.file_path, file_path)
    elif message.document:
        file_id = message.document.file_id
        if message.document.file_size > 20 * 1024 * 1024:
            await message.answer(TEXTS[lang]["file_too_large"])
            return
        file = await bot.get_file(file_id)
        file_name = message.document.file_name
        file_path = f"media/documents/{file_id}_{file_name}"
        await bot.download_file(file.file_path, file_path)

    await state.update_data(diplom_fayl=file_path)
    
    # Check if we need certificate
    data = await state.get_data()
    yonalish = data.get("yonalish", "")
    if "English" in yonalish or "ingliz" in yonalish.lower():
        await message.answer(TEXTS[lang]["ask_certificate"], parse_mode="HTML")
        await state.set_state(AdmissionForm.sertifikat_fayl)
    else:
        await state.update_data(sertifikat_fayl="")
        data = await state.get_data()
        await show_confirmation(message, data, state)

@router.message(AdmissionForm.sertifikat_fayl, F.photo | F.document)
async def process_sertifikat(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "uz")
    bot = message.bot
    if message.photo:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = f"media/photos/{file_id}.jpg"
        await bot.download_file(file.file_path, file_path)
    elif message.document:
        file_id = message.document.file_id
        if message.document.file_size > 20 * 1024 * 1024:
            await message.answer(TEXTS[lang]["file_too_large"])
            return
        file = await bot.get_file(file_id)
        file_name = message.document.file_name
        file_path = f"media/documents/{file_id}_{file_name}"
        await bot.download_file(file.file_path, file_path)

    await state.update_data(sertifikat_fayl=file_path)
    data = await state.get_data()
    await show_confirmation(message, data, state)

async def show_confirmation(message: Message, data: dict, state: FSMContext):
    lang = data.get("language", "uz")
    text = TEXTS[lang]["confirmation"].format(
        ism=data.get('ism'),
        familiya=data.get('familiya'),
        otasining_ismi=data.get('otasining_ismi'),
        telefon=data.get('telefon'),
        yonalish=data.get('yonalish')
    )
    await message.answer(text, parse_mode="HTML", reply_markup=tasdiqlash_keyboard(lang))
    await state.set_state(AdmissionForm.tasdiqlash)

@router.callback_query(AdmissionForm.tasdiqlash, F.data.startswith("tasdiq_"))
async def process_tasdiqlash(callback: CallbackQuery, state: FSMContext):
    tasdiq = callback.data.split("_")[1]
    data = await state.get_data()
    lang = data.get("language", "uz")
    if tasdiq == "ha":
        await save_user_data(callback.from_user.id, data)
        await callback.message.edit_text(TEXTS[lang]["success"], parse_mode="HTML")
        await state.clear()
        
        try:
            from database.db import get_group_id
            dyn_group = await get_group_id()
            target_id = dyn_group if dyn_group else ADMIN_ID
            admin_msg = f"<b>🔔 Yangi ariza tushdi!</b>\n\n<b>F.I.O:</b> {data.get('ism')} {data.get('familiya')}\n<b>Yo'nalish:</b> {data.get('yonalish')}\n<b>Aloqa:</b> {data.get('telefon')}"
            await callback.bot.send_message(chat_id=target_id, text=admin_msg, parse_mode="HTML")
        except:
            pass
    else:
        await reset_user(callback.from_user.id)
        await callback.message.edit_text(TEXTS[lang]["cancelled"], parse_mode="HTML")
        await state.clear()
