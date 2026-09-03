import sys
import os
import re
import requests
import pyautogui
import pytesseract
import keyboard
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextBrowser, QPushButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Tesseract-OCR manzili
pytesseract.pytesseract.tesseract_cmd = r'D:\ilovalar\Tesseract-OCR\tesseract.exe'
API_URL = "http://127.0.0.1:8000/api/v1/diagnostics/analyze/"


class CaptureThread(QThread):
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def run(self):
        try:
            screenshot = pyautogui.screenshot()
            screenshot_path = "scanmatik_temp.png"
            screenshot.save(screenshot_path)

            raw_text = pytesseract.image_to_string(Image.open(screenshot_path))
            dtc_pattern = r'[P|C|B|U]\d{4}'
            found_codes = list(set(re.findall(dtc_pattern, raw_text)))

            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

            payload = {
                "car_model": "Ekrandan aniqlanmoqda",
                "dtc_codes": found_codes,
                "raw_text": raw_text
            }

            response = requests.post(API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                self.finished_signal.emit(response.json())
            else:
                self.error_signal.emit(f"Server xatosi: STATUS {response.status_code}")
        except Exception as e:
            self.error_signal.emit(f"Ulanishda xatolik: {str(e)}")
