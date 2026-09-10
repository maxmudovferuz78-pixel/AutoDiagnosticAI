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

        if self.is_selecting:
            select_rect = QRect(self.begin, self.end).normalized()

            # Tanlangan joyni ravshan qilib ko'rsatish
            # Scale ratio hisobga olingan holda pixmap qirqish rect-i:
            crop_rect = QRect(
                int(select_rect.x() * self.device_ratio),
                int(select_rect.y() * self.device_ratio),
                int(select_rect.width() * self.device_ratio),
                int(select_rect.height() * self.device_ratio)
            )

            cropped_sub = self.screen_pixmap.copy(crop_rect)
            painter.drawPixmap(select_rect, cropped_sub)

            pen = QPen(QColor('#0056b3'), 2)
            painter.setPen(pen)
            painter.drawRect(select_rect)

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
            select_rect = QRect(self.begin, self.end).normalized()

            if select_rect.width() > 10 and select_rect.height() > 10:
                # Haqiqiy piksel o'lchamida qirqib olish
                real_crop_rect = QRect(
                    int(select_rect.x() * self.device_ratio),
                    int(select_rect.y() * self.device_ratio),
                    int(select_rect.width() * self.device_ratio),
                    int(select_rect.height() * self.device_ratio)
                )
                cropped = self.screen_pixmap.copy(real_crop_rect)
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

        layout = QVBoxLayout()
        title = QLabel("⚡ AutoDiagnostic AI Assistant")
        layout.addWidget(title)

        self.text_area = QTextBrowser()
        self.text_area.setHtml(
            "<p style='color: #6C757D;'>Tahlilni boshlash uchun <b>Alt + A</b> ni bosing va ekrandagi xatolik kodini tanlang.</p>"
        )
        layout.addWidget(self.text_area)

        close_btn = QPushButton("Oynani yopish (Esc)")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

        self.setLayout(layout)

