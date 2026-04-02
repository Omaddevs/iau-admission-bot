from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.regions import regions_data

def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )

def yonalish_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="BSc Agroeconomics | English", callback_data="yonalish_BSc_Agroeconomics_EN")],
            [InlineKeyboardButton(text="BSc Agrologistics | English", callback_data="yonalish_BSc_Agrologistics_EN")],
            [InlineKeyboardButton(text="BSc Food Safety Management | English", callback_data="yonalish_BSc_FoodSafetyMgmt_EN")],
            [InlineKeyboardButton(text="BSc Smart Sustainable Agriculture | English", callback_data="yonalish_BSc_SmartSusAgric_EN")],
            [InlineKeyboardButton(text="BSc Business Management (subject to validation) | English", callback_data="yonalish_BSc_BusinessMgmt_EN")],
            [InlineKeyboardButton(text="MSc Agri-Business Management | English", callback_data="yonalish_MSc_AgriBusinessMgmt_EN")],
            [InlineKeyboardButton(text="MSc Sustainable Agriculture and Food Security | English", callback_data="yonalish_MSc_SusAgricFoodSec_EN")],
            [InlineKeyboardButton(text="Iqtisodiyot (Kunduzgi) | O'zbek", callback_data="yonalish_Iqtisodiyot_Kunduzgi_UZ")],
            [InlineKeyboardButton(text="Iqtisodiyot (Masofaviy) | O'zbek", callback_data="yonalish_Iqtisodiyot_Masofaviy_UZ")],
            [InlineKeyboardButton(text="Agronomiya (Kunduzgi) | O'zbek", callback_data="yonalish_Agronomiya_Kunduzgi_UZ")],
            [InlineKeyboardButton(text="Oziq-ovqat texnologiyasi (Kunduzgi) | O'zbek", callback_data="yonalish_Oziq_ovqat_Kunduzgi_UZ")],
            [InlineKeyboardButton(text="Biologiya (Kunduzgi) | O'zbek", callback_data="yonalish_Biologiya_Kunduzgi_UZ")],
            [InlineKeyboardButton(text="Filologiya va tillarni o'qitish: ingliz tili (Kunduzgi) | O'zbek", callback_data="yonalish_Filologiya_Kunduzgi_UZ")]
        ]
    )

def msc_shakl_keyboard(lang="uz"):
    from utils.texts import TEXTS
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["full_time"], callback_data="msc_Full_time")],
            [InlineKeyboardButton(text=TEXTS[lang]["part_time"], callback_data="msc_Part_time")]
        ]
    )
def regions_keyboard():
    keyboard = []
    # Display 2 regions per row
    regions_list = list(regions_data.keys())
    for i in range(0, len(regions_list), 2):
        row = []
        row.append(InlineKeyboardButton(text=regions_list[i], callback_data=f"region_{regions_list[i]}"))
        if i + 1 < len(regions_list):
            row.append(InlineKeyboardButton(text=regions_list[i+1], callback_data=f"region_{regions_list[i+1]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def districts_keyboard(region_name):
    keyboard = []
    districts = regions_data.get(region_name, [])
    for i in range(0, len(districts), 2):
        row = []
        row.append(InlineKeyboardButton(text=districts[i], callback_data=f"district_{districts[i]}"))
        if i + 1 < len(districts):
            row.append(InlineKeyboardButton(text=districts[i+1], callback_data=f"district_{districts[i+1]}"))
        keyboard.append(row)
    # Give a back button maybe? Not necessarily req.
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def tasdiqlash_keyboard(lang="uz"):
    from utils.texts import TEXTS
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["confirm_yes"], callback_data="tasdiq_ha")],
            [InlineKeyboardButton(text=TEXTS[lang]["confirm_no"], callback_data="tasdiq_yoq")]
        ]
    )

def admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="🟡 Jarayonda qolganlar", callback_data="admin_qolganlar")],
            [InlineKeyboardButton(text="📂 Arizalar", callback_data="admin_arizalar")],
            [InlineKeyboardButton(text="📥 Excel yuklab olish", callback_data="admin_excel")],
            [InlineKeyboardButton(text="📨 Xabar yuborish", callback_data="admin_xabar")]
        ]
    )

def xabar_turi_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Barchaga", callback_data="xabar_barchaga")],
            [InlineKeyboardButton(text="👤 Bitta userga", callback_data="xabar_bittaga")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")]
        ]
    )

def arizalar_list_keyboard(users):
    keyboard = []
    for user in users:
        ism = user['ism'] or ""
        fam = user['familiya'] or ""
        ota = user['otasining_ismi'] or ""
        name = f"{ism} {fam} {ota}".strip()
        if not name:
            name = f"Yangi user (ID: {user['telegram_id']})"
        keyboard.append([InlineKeyboardButton(text=f"👉 {name}", callback_data=f"user_{user['telegram_id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def user_detail_keyboard(telegram_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📨 Xabar yuborish", callback_data=f"msguser_{telegram_id}")],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"deluser_{telegram_id}")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")]
        ]
    )

def back_to_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_menu")]
        ]
    )
