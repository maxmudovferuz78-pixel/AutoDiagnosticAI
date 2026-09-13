import sys
import os
import re
import requests
import pytesseract
import keyboard
import ctypes

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextBrowser, QPushButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap

# Windows DPI scaling masshtab muammosini aniq to'g'rilash (Windows 8.1 va undan yuqori)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Tesseract-OCR manzilini tekshirish
possible_paths = [
    r'D:\ilovalar\Tesseract-OCR\tesseract.exe',
    r'D:\ilovalar\tesseract.exe',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
]
for path in possible_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

API_URL = "http://127.0.0.1:8000/api/v1/diagnostics/analyze/"


class HotkeySignaler(QObject):
    triggered = pyqtSignal()


hotkey_signaler = HotkeySignaler()


# Skrinshot qirqib olish oynasi (Windows+Shift+S)
class SnippingWidget(QWidget):
    area_selected = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
