from openpyxl import Workbook
import os
from datetime import datetime

def export_users_to_excel(users, filename="arizalar.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Arizalar"

    # Headers
    headers = [
        "Ism", "Familiya", "Otasining ismi", "Telefon", "Email",
        "Viloyat & Tuman", "Pasport", "Tug'ilgan sana", "Yo'nalish", "Telegram User ID"
    ]
    ws.append(headers)

    for user in users:
        manzil = f"{user['manzil_viloyat']}, {user['manzil_tuman']}"
        row = [
            user['ism'],
            user['familiya'],
            user['otasining_ismi'],
            user['telefon'],
            user['email'],
            manzil,
            user['pasport_raqam'],
            user['tugilgan_sana'],
            user['yonalish'],
            user['telegram_id']
        ]
        ws.append(row)

    filepath = os.path.join("media", "exports", filename)
    wb.save(filepath)
    return filepath
