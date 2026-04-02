import zipfile
import os

def create_user_archive(user_data):
    user_data = dict(user_data)
    ism = user_data.get('ism') or "User"
    familiya = user_data.get('familiya') or str(user_data.get('telegram_id', 'Unknown'))
    ota = user_data.get('otasining_ismi') or ""
    
    # Form filename: Ism_Familiya_Otasining_ismi.zip
    file_name = f"{ism}_{familiya}_{ota}".strip().replace(" ", "_") + ".zip"
    output_path = f"media/archives/{file_name}"
    
    with zipfile.ZipFile(output_path, 'w') as zipf:
        # Pasport
        if user_data.get('pasport_fayl') and os.path.exists(user_data['pasport_fayl']):
            zipf.write(user_data['pasport_fayl'], arcname=f"pasport_{os.path.basename(user_data['pasport_fayl'])}")
        # Diplom
        if user_data.get('diplom_fayl') and os.path.exists(user_data['diplom_fayl']):
            zipf.write(user_data['diplom_fayl'], arcname=f"diplom_{os.path.basename(user_data['diplom_fayl'])}")
        # Sertifikat
        if user_data.get('sertifikat_fayl') and os.path.exists(user_data['sertifikat_fayl']):
            zipf.write(user_data['sertifikat_fayl'], arcname=f"sertifikat_{os.path.basename(user_data['sertifikat_fayl'])}")
            
    return output_path
