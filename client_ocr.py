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

