import json
import os
from google import genai
from google.genai import types
from django.conf import settings

# Gemini Client ni sozlaymiz
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_ai_diagnostic_analysis(car_model: str, dtc_codes: list, raw_text: str = "") -> dict:
    """
    Gemini AI yordamida Scanmatik diagnostika natijalarini
    o'zbek tilida professional tahlil qilib beradi.
    """

    system_prompt = """
    Siz O'zbekiston avtomobil bozori bo'yicha professional avtoelektrik va diagnostik-muhandissiz.
    Sizga avtomobil modeli, xatolik kodlari (DTC) va skanerdan olingan text beriladi.

    Javobingizni har doim va FAQAT quyidagi JSON formatida qaytaring:
    {
        "status": "success",
        "car_model": "Mashina modeli",
        "translated_codes": [
            {"code": "P0300", "description": "Ko'p silindrlarda yonish o'tkazib yuborildi"}
        ],
        "possible_causes": [
            "1. Svecha yoki babina simlarida nosozlik (Cobalt/Gentra uchun eng ko'p uchraydi)",
            "2. Yonilg'i bosimi pastligi yoki purkagichlar (forsunka) tiqilishi"
        ],
        "step_by_step_fix": [
            "1-qadam: Svecha simlarining qarshiligini multimetr bilan o'lchang.",
            "2-qadam: Yonilg'i mantiqiy bosimini manometer orqali tekshiring."
        ],
        "note": "Gaz apparati (GBO) o'rnatilgan bo'lsa, gaz reduktorining havo so'rishini ham ko'ring."
    }

    Qoidalar:
    - Faqat o'zbek tilida (lotin alifbosida) javob bering.
    - Qisqa, amaliy va ustaga darhol tushunarli punktlar yozing.
    - Mahalliy bozor spetsifikatsiyasini (Cobalt, Gentra, Nexia, Damas, BYD, gaz-benzin tizimi) hisobga oling.
    """

