
import json


BOOLEAN_FIELDS = {
    "verified",
    "busy",
    "callback_requested",
    "transfer_intent",
    "documents_available",
    "max_amount_accepted",
}

STRING_FIELDS = {
    "customer_name",
    "callback_time",
}

ENUM_FIELDS = {
    "property_type": {
        "RESIDENTIAL",
        "COMMERCIAL",
        "INDUSTRIAL",
        "AGRICULTURAL",
    },
    "ownership_status": {"SOLE", "JOINT"},
    "occupation": {"SALARIED", "SELF_EMPLOYED"},
    "income_mode": {"BANK", "CASH"},
}

NUMBER_FIELDS = {"loan_amount", "market_value"}
INTEGER_FIELDS = {"tenure"}

ALLOWED_FIELDS = (
    BOOLEAN_FIELDS
    | STRING_FIELDS
    | set(ENUM_FIELDS)
    | NUMBER_FIELDS
    | INTEGER_FIELDS
)


def validate_extracted_answers(raw_answers):
    """Validate a dictionary or JSON string of extracted answers."""

    if isinstance(raw_answers, str):
        try:
            raw_answers = json.loads(raw_answers)
        except json.JSONDecodeError as exc:
            raise ValueError("Extractor output must be valid JSON.") from exc

    if not isinstance(raw_answers, dict):
        raise ValueError("Extractor output must be a JSON object.")

    unknown_fields = set(raw_answers) - ALLOWED_FIELDS
    if unknown_fields:
        raise ValueError(
            f"Unknown fields: {', '.join(sorted(unknown_fields))}"
        )

    cleaned = {}

    for field, value in raw_answers.items():
        if value is None:
            cleaned[field] = None
            continue

        if field in BOOLEAN_FIELDS:
            if not isinstance(value, bool):
                raise ValueError(f"{field} must be true, false, or null.")
            cleaned[field] = value

        elif field in STRING_FIELDS:
            if not isinstance(value, str):
                raise ValueError(f"{field} must be a string or null.")
            cleaned[field] = value.strip()

        elif field in ENUM_FIELDS:
            if not isinstance(value, str):
                raise ValueError(f"{field} must be a string or null.")

            normalized = value.strip().upper().replace("-", "_").replace(" ", "_")

            if normalized not in ENUM_FIELDS[field]:
                raise ValueError(
                    f"Invalid value for {field}: {value!r}"
                )

            cleaned[field] = normalized

        elif field in NUMBER_FIELDS:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{field} must be a number or null.")

            if value <= 0:
                raise ValueError(f"{field} must be greater than zero.")

            cleaned[field] = value

        elif field in INTEGER_FIELDS:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{field} must be an integer or null.")

            cleaned[field] = value

    return cleaned
