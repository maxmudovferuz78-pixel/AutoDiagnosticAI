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
