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

