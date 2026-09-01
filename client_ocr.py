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
