import os
import re
import time
import requests
import pyautogui
import easyocr
import keyboard

# EasyOCR reader-ni yaratamiz (ingliz va rus tillari uchun)
print("[+] OCR Engine yuklanmoqda...")
reader = easyocr.Reader(['en', 'ru'], gpu=False)

API_URL = "http://127.0.0.1:8000/api/v1/diagnostics/analyze/"


def capture_and_analyze():
    print("\n[+] Skrinshot olinmoqda va tahlil qilinmoqda...")

    # 1. Ekran skrinshotini olamiz
    screenshot = pyautogui.screenshot()
    screenshot_path = "scanmatik_temp.png"
    screenshot.save(screenshot_path)

    # 2. EasyOCR orqali matnni o'qiymiz
    results = reader.readtext(screenshot_path, detail=0)
    raw_text = " ".join(results)

    # 3. DTC xatolik kodlarini (P0300, P0171, C0035 va h.k.) qidiramiz
    dtc_pattern = r'[P|C|B|U]\d{4}'
    found_codes = list(set(re.findall(dtc_pattern, raw_text)))

    print(f"[✓] Topilgan DTC kodlar: {found_codes}")
    print(f"[✓] O'qilgan matn: {raw_text[:120]}...")

    # 4. Backend API'ga so'rov yuboramiz
    payload = {
        "car_model": "Ekrandan aniqlanmoqda",
        "dtc_codes": found_codes,
        "raw_text": raw_text
    }
