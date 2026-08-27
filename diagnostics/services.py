import json
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_ai_diagnostic_analysis(car_model: str, dtc_codes: list, raw_text: str = "") -> dict:
    """
    DTC xatolik kodlari va mashina modelini qabul qilib,
    AI orqali o'zbek tilida diagnostika xulosasini tayyorlaydi.
    """

    system_prompt = """
    Siz O'zbekiston avtomobil bozori bo'yicha professional avtoelektrik va diagnostik-muhandissiz.
    Sizga avtomobil modeli, xatolik kodlari (DTC) yoki skanerdan olingan xom matn beriladi.

    Javobingizni har doim quyidagi JSON formatida qaytaring:
    {
        "status": "success",
        "translated_codes": [
            {"code": "P0300", "description": "Ko'p silindrlarda yonish o'tkazib yuborildi"}
        ],
        "possible_causes": [
            "1-sabab...",
            "2-sabab..."
        ],
        "step_by_step_fix": [
            "1-qadam...",
            "2-qadam..."
        ],
        "note": "Aynan shu mashina modeli uchun qo'shimcha maxsus eslatma"
    }

    Qoidalar:
    - Javob faqat o'zbek tilida (lotin alifbosida) bo'lsin.
    - Uzun matnlar yozmang, ustaga tez va amaliy yechim kerak.
    - O'zbekistondagi eng ko'p uchraydigan holatlarni (masalan, Gaz/Benzin, svecha simlari, babina, yonilg'i bosimi, havo so'rish) inobatga oling.
    """

    user_prompt = f"""
    Avtomobil modeli: {car_model if car_model else "Noma'lum"}
    Xatolik kodlari: {', '.join(dtc_codes)}
    Xom matn (OCR): {raw_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        result_json = json.loads(response.choices[0].message.content)
        return result_json

    except Exception as e:
        return {
            "status": "error",
            "message": f"AI tahlilida xatolik yuz berdi: {str(e)}"
        }