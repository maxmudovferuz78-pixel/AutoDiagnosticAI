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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()


# Serverga so'rov yuborish
class CaptureThread(QThread):
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, pixmap):
        super().__init__()
        self.pixmap = pixmap

    def run(self):
        try:
            temp_path = "snip_temp.png"
            self.pixmap.save(temp_path)

            from PIL import Image
            raw_text = pytesseract.image_to_string(Image.open(temp_path))
            dtc_pattern = r'[P|C|B|U]\d{4}'
            found_codes = list(set(re.findall(dtc_pattern, raw_text)))

            if os.path.exists(temp_path):
                os.remove(temp_path)

            payload = {
                "car_model": "Ekrandan aniqlanmoqda",
                "dtc_codes": found_codes,
                "raw_text": raw_text
            }

            response = requests.post(API_URL, json=payload, timeout=30)
            if response.status_code == 200:
                self.finished_signal.emit(response.json())
            else:
                self.error_signal.emit(f"Server xatosi: STATUS {response.status_code}")
        except requests.exceptions.Timeout:
            self.error_signal.emit("AI tahlil qilishga ulgurmadi (Timeout). Qaytadan urinib ko'ring.")
        except Exception as e:
            self.error_signal.emit(f"Ulanishda xatolik: {str(e)}")


# Oq fondagi asosiy diagnostika oynasi
class DiagnosticOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.snipper = SnippingWidget()
        self.snipper.area_selected.connect(self.process_cropped_image)

    def init_ui(self):
        self.setWindowTitle("AutoDiagnostic AI Assistant")
        self.setGeometry(100, 100, 480, 600)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # To'liq OQ FON (Light theme) stili
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #212529;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0D6EFD;
                padding: 4px;
            }
            QTextBrowser {
                background-color: #F8F9FA;
                border: 1px solid #CED4DA;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                color: #212529;
            }
            QPushButton {
                background-color: #DC3545;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #BB2D3B;
            }
        """)

