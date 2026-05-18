import re

from utils.config import VALID_SHIFT_VALUES, MAX_QUANTITY, MAX_TIME_HOURS


def validate_extraction(extraction_id, data, existing_extractions=None):
    flags = []

    flags.extend(_validate_missing_fields(data))
    flags.extend(_validate_shift(data))
    flags.extend(_validate_numeric_fields(data))
    flags.extend(_validate_machine_code(data))
    flags.extend(_validate_work_order_duplicate(data, existing_extractions))

    return flags


def _validate_missing_fields(data):
    flags = []
    mandatory_fields = {
        "date": "Date",
        "shift": "Shift",
        "employee_number": "Employee Number",
        "operation_code": "Operation Code",
        "work_order_number": "Work Order Number",
    }
    for field, label in mandatory_fields.items():
        value = data.get(field, "").strip()
        if not value or value == "":
            flags.append({
                "field": field,
                "issue_type": "missing",
                "message": f"{label} is missing",
            })
    return flags


def _validate_shift(data):
    flags = []
    shift = data.get("shift", "").strip()
    if shift and shift not in VALID_SHIFT_VALUES:
        flags.append({
            "field": "shift",
            "issue_type": "invalid_shift",
            "message": f"Invalid shift value: '{shift}'. Expected 1, 2, or 3",
        })
    return flags


def _validate_numeric_fields(data):
    flags = []
    qty = data.get("quantity_produced", "").strip()
    if qty:
        try:
            qty_val = int(qty)
            if qty_val <= 0:
                flags.append({
                    "field": "quantity_produced",
                    "issue_type": "suspicious_value",
                    "message": f"Quantity produced is zero or negative: {qty_val}",
                })
            elif qty_val > MAX_QUANTITY:
                flags.append({
                    "field": "quantity_produced",
                    "issue_type": "suspicious_value",
                    "message": f"Quantity produced ({qty_val}) exceeds maximum expected ({MAX_QUANTITY})",
                })
        except ValueError:
            flags.append({
                "field": "quantity_produced",
                "issue_type": "invalid_format",
                "message": f"Quantity produced '{qty}' is not a valid number",
            })
    else:
        flags.append({
            "field": "quantity_produced",
            "issue_type": "missing",
            "message": "Quantity Produced: the given value is empty",
        })

    time_taken = data.get("time_taken", "").strip()
    if time_taken:
        try:
            time_val = float(time_taken)
            if time_val <= 0:
                flags.append({
                    "field": "time_taken",
                    "issue_type": "suspicious_value",
                    "message": f"Time taken is zero or negative: {time_val}",
                })
            elif time_val > MAX_TIME_HOURS:
                flags.append({
                    "field": "time_taken",
                    "issue_type": "suspicious_value",
                    "message": f"Time taken ({time_val}h) exceeds maximum expected ({MAX_TIME_HOURS}h)",
                })
        except ValueError:
            flags.append({
                "field": "time_taken",
                "issue_type": "invalid_format",
                "message": f"Time taken '{time_taken}' is not a valid number",
            })

    return flags


def _validate_machine_code(data):
    flags = []
    machine = data.get("machine_number", "").strip()
    if machine:
        if not re.match(r'^[A-Za-z0-9\-/]+$', machine):
            flags.append({
                "field": "machine_number",
                "issue_type": "invalid_format",
                "message": f"Machine number '{machine}' contains invalid characters",
            })
    return flags


def _validate_work_order_duplicate(data, existing_extractions):
    flags = []
    wo = data.get("work_order_number", "").strip()
    if wo and existing_extractions:
        for ext in existing_extractions:
            ext_wo = ext.get("work_order_number", "").strip()
            if ext_wo == wo:
                flags.append({
                    "field": "work_order_number",
                    "issue_type": "duplicate",
                    "message": f"Work order number '{wo}' already exists in another record",
                })
                break
    return flags
