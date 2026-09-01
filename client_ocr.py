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

