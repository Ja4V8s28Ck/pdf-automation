import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

VALID_SHIFT_VALUES = {"1", "2", "3"}
MAX_QUANTITY = 99999
MAX_TIME_HOURS = 24
MIN_TIME_HOURS = 0.1

EXTRACTION_FIELDS = [
    "date",
    "shift",
    "employee_number",
    "operation_code",
    "machine_number",
    "work_order_number",
    "quantity_produced",
    "time_taken",
]

FIELD_LABELS = {
    "date": "Date",
    "shift": "Shift",
    "employee_number": "Employee Number",
    "operation_code": "Operation Code",
    "machine_number": "Machine Number",
    "work_order_number": "Work Order Number",
    "quantity_produced": "Quantity Produced",
    "time_taken": "Time Taken",
}
