from aiogram.fsm.state import StatesGroup, State

class AdmissionForm(StatesGroup):
    language = State()
    ism = State()
    familiya = State()
    otasining_ismi = State()
    telefon = State()
    email = State()
    manzil_viloyat = State()
    manzil_tuman = State()
    pasport_raqam = State()
    pasport_fayl = State()
    tugilgan_sana = State()
    diplom_fayl = State()
    yonalish = State()
    msc_shakl = State()
    sertifikat_fayl = State()
    tasdiqlash = State()

class AdminMessage(StatesGroup):
    barchaga = State()
    bittaga_id = State()
    bittaga_xabar = State()
