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
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        self.screen_pixmap = None

    def start_snipping(self):
        screen = QApplication.primaryScreen()
        if screen:
            self.screen_pixmap = screen.grabWindow(0)
            self.setGeometry(screen.geometry())
            self.show()
            self.activateWindow()

    def paintEvent(self, event):
        if not self.screen_pixmap:
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.screen_pixmap)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.is_selecting:
            rect = QRect(self.begin, self.end).normalized()
            painter.drawPixmap(rect, self.screen_pixmap, rect)
            pen = QPen(QColor('#0056b3'), 2)
            painter.setPen(pen)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.hide()
            rect = QRect(self.begin, self.end).normalized()
            if rect.width() > 10 and rect.height() > 10:
                cropped = self.screen_pixmap.copy(rect)
                self.area_selected.emit(cropped)

