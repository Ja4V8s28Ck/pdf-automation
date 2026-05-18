import json
from google import genai

from utils.config import GEMINI_API_KEY, GEMINI_MODEL

EXTRACTION_PROMPT = """You are an OCR assistant for manufacturing operational documents.
Analyze this image of a handwritten manufacturing form and extract ALL data entries/rows visible.

For each entry, extract these fields:
- date: The date shown (use YYYY-MM-DD format; if only day/month visible, infer year from context)
- shift: The shift number (1, 2, or 3)
- employee_number: Employee ID or number
- operation_code: Operation code
- machine_number: Machine number or code
- work_order_number: Work order / job order number
- quantity_produced: Quantity produced (numeric value only)
- time_taken: Time taken (numeric value, in hours if specified)

For EACH field, provide a confidence score between 0.0 and 1.0:
- 0.0 = field is empty, illegible, or not present
- 0.1-0.4 = barely legible, highly uncertain
- 0.5-0.7 = partially legible, some uncertainty
- 0.8-0.9 = mostly legible, minor uncertainty
- 1.0 = perfectly clear and certain

If a field is empty or not visible in the image, set value to "" and confidence to 0.0.

Return ONLY valid JSON with NO markdown formatting, NO code blocks, in this exact format:
{"records":[{"date":{"value":"...","confidence":0.0},"shift":{"value":"...","confidence":0.0},"employee_number":{"value":"...","confidence":0.0},"operation_code":{"value":"...","confidence":0.0},"machine_number":{"value":"...","confidence":0.0},"work_order_number":{"value":"...","confidence":0.0},"quantity_produced":{"value":"...","confidence":0.0},"time_taken":{"value":"...","confidence":0.0}}]}

If no records are visible, return {"records":[]}."""


def _parse_response(response):
    text = response.text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(text)
    records = parsed.get("records", [])
    result = []
    for record in records:
        row = {}
        confidence = {}
        for field in ["date", "shift", "employee_number", "operation_code",
                       "machine_number", "work_order_number",
                       "quantity_produced", "time_taken"]:
            field_data = record.get(field, {})
            if isinstance(field_data, dict):
                row[field] = str(field_data.get("value", "")).strip()
                conf = field_data.get("confidence", 0.0)
                confidence[field] = round(float(conf), 2)
            else:
                row[field] = str(field_data).strip()
                confidence[field] = 0.0
        result.append((row, confidence))
    return result


def extract_from_image(image_path):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=GEMINI_API_KEY)
    uploaded_file = client.files.upload(file=image_path)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[EXTRACTION_PROMPT, uploaded_file],
    )
    return _parse_response(response)
