import sys
import os
import re
import requests
import pytesseract
import keyboard
import ctypes

# 1. QApplication yaratilishidan avval Windows DPI awareness-ni sozlaymiz
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Process_Per_Monitor_DPI_Aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextBrowser, QPushButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap

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


# Skrinshot qirqib olish oynasi (Windows+Shift+S kabi)
class SnippingWidget(QWidget):
    area_selected = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        self.screen_pixmap = None
        self.device_ratio = 1.0

    def start_snipping(self):
        screen = QApplication.primaryScreen()
        if screen:
            self.device_ratio = screen.devicePixelRatio()  # Ekran masshtabi nisbati (masalan, 1.25 yoki 1.5)
            self.screen_pixmap = screen.grabWindow(0)
            self.setGeometry(screen.geometry())
            self.show()
            self.activateWindow()

    def paintEvent(self, event):
        if not self.screen_pixmap:
            return
        painter = QPainter(self)

        # Ekran doirasini to'g'ri chizish
        rect = self.rect()
        painter.drawPixmap(rect, self.screen_pixmap)
        painter.fillRect(rect, QColor(0, 0, 0, 100))
