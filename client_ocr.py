import os
import re
import time
import requests
import pyautogui
import pytesseract
import keyboard
from PIL import Image

# Agar Tesseract C drive ga o'rnatilgan bo'lsa, manzilni ko'rsatamiz:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Bizning Django Backend API Manzili
API_URL = "http://127.0.0.1:8000/api/v1/diagnostics/analyze/"


def capture_and_analyze():
    print("\n[+] Skrinshot olinmoqda va tahlil qilinmoqda...")

    # 1. Ekran skrinshotini olamiz
    screenshot = pyautogui.screenshot()
    screenshot_path = "scanmatik_temp.png"
    screenshot.save(screenshot_path)

    # 2. OCR yordamida ekrandagi matnlarni o'qiymiz
    raw_text = pytesseract.image_to_string(Image.open(screenshot_path))

    # 3. Regex orqali DTC xatolik kodlarini (Masalan: P0300, P0171, C0035, U0100) ajratib olamiz
    dtc_pattern = r'[P|C|B|U]\d{4}'
    found_codes = list(set(re.findall(dtc_pattern, raw_text)))

    print(f"[✓] Topilgan DTC kodlar: {found_codes}")
    print(f"[✓] Ekrandan o'qilgan xom matn qisqartmasi: {raw_text[:100]}...")

    # 4. Django REST Backend API'ga so'rov yuboramiz
    payload = {
        "car_model": "Ekrandan aniqlanmoqda",  # Kelajakda avto-modelni ham OCR qilamiz
        "dtc_codes": found_codes,
        "raw_text": raw_text
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("\n================= AI TAHLIL NATIJASI =================")
            print(f"Mashina: {result.get('car_model')}")
            print("\n[Tarjima va Kodlar]:")
            for item in result.get('translated_codes', []):
                print(f"  • {item.get('code')}: {item.get('description')}")

            print("\n[Ehtimoliy Sabablar]:")
            for cause in result.get('possible_causes', []):
                print(f"  • {cause}")

            print("\n[Tekshirish Ketma-ketligi]:")
            for step in result.get('step_by_step_fix', []):
                print(f"  • {step}")

            print("\n[Eslatma]:", result.get('note'))
            print("======================================================")
        else:
            print("[-] API Xatolik qaytardi:", response.status_code)
    except Exception as e:
        print("[-] Server bilan ulanishda xatolik:", str(e))
