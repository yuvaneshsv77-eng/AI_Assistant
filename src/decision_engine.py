
"""Decision engine for the Home Credit LAP qualification agent.

This module evaluates structured customer data.
Natural-language extraction and voice integration will be added separately.
"""

from copy import deepcopy

MAX_LOAN_AMOUNT = 7_500_000  # ₹75 lakh
MIN_TENURE = 3
MAX_TENURE = 15

# Seven checklist items; occupation and income mode are separate fields.
QUESTION_ORDER = [
    ("property_type", "ASK_PROPERTY_TYPE"),
    ("ownership_status", "ASK_OWNERSHIP"),
    ("documents_available", "ASK_DOCUMENTS"),
    ("loan_amount", "ASK_LOAN_AMOUNT"),
    ("occupation", "ASK_OCCUPATION_AND_INCOME_MODE"),
    ("income_mode", "ASK_OCCUPATION_AND_INCOME_MODE"),
    ("market_value", "ASK_MARKET_VALUE"),
    ("tenure", "ASK_TENURE"),
]


def initial_state():
    """Return a fresh customer state for a new call."""
    return {
        "customer": {
            "name": None,
            "verified": False,
        },
        "eligibility": {
            "property_type": None,
            "ownership_status": None,
            "documents_available": None,
            "loan_amount": None,
            "occupation": None,
            "income_mode": None,
            "market_value": None,
            "tenure": None,
        },
        "flow": {
            "current_question": None,
            "transfer_intent": False,
            "disqualified": False,
            "handoff_allowed": False,
            "call_status": "IN_PROGRESS",
            "max_amount_offer_pending": False,
            "max_amount_accepted": False,
        },
        "decision": {
            "status": "PENDING",
            "reason": None,
        },
    }


def normalize_value(value):
    """Normalize supported categorical answers for rule evaluation."""
    if not isinstance(value, str):
        return value

    return value.strip().upper().replace("-", "_").replace(" ", "_")


def get_missing_field(eligibility):
    """Return the first unanswered field in the specified question order."""
    for field, _ in QUESTION_ORDER:
        value = eligibility.get(field)

        if value is None or value == "":
            return field

    return None


def get_next_question(field):
    """Map an unanswered field to the action that asks its question."""
    for current_field, action in QUESTION_ORDER:
        if field == current_field:
            return action

    return None


def evaluate_state(state):
    """Evaluate a customer state and return the next decision/action.

    The input state is not modified. The caller owns state updates.
    """
    result_state = deepcopy(state)
    eligibility = result_state["eligibility"]
    flow = result_state["flow"]
    


    def result(status, action, reason=None, end_call=False):
        result_state["decision"]["status"] = status
        result_state["decision"]["reason"] = reason
        result_state["flow"]["handoff_allowed"] = (
            action == "QUALIFIED_FOR_HANDOFF"
        )
        result_state["flow"]["disqualified"] = (
    status == "DISQUALIFIED"
)

        if end_call:
            result_state["flow"]["call_status"] = "COMPLETED"

        return {
            "updated_state": result_state,
            "decision": {
                "status": status,
                "reason": reason,
            },
            "next_action": action,
        }

    # 1. Transfer intent takes priority over normal qualification.
    if flow.get("transfer_intent") is True:
        return result(
            "TRANSFER_REQUIRED",
            "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST",
            "Existing property loan, EMI reduction, or transfer request.",
            end_call=True,
        )

    # 2. Apply immediate disqualification rules.
    property_type = normalize_value(eligibility.get("property_type"))
    income_mode = normalize_value(eligibility.get("income_mode"))
    documents = normalize_value(eligibility.get("documents_available"))
    tenure = eligibility.get("tenure")

    if property_type == "AGRICULTURAL":
        return result(
            "DISQUALIFIED",
            "DISQUALIFY",
            "Agricultural property is not eligible for this offer.",
            end_call=True,
        )

    if income_mode == "CASH":
        return result(
            "DISQUALIFIED",
            "DISQUALIFY",
            "Cash income is not eligible for this offer.",
            end_call=True,
        )

    if documents is False or documents in {
    "NO",
    "NOT_AVAILABLE",
    "FALSE",
}:
        return result(
            "DISQUALIFIED",
            "DISQUALIFY",
            "Original property documents are not available.",
            end_call=True,
        )

    if isinstance(tenure, (int, float)) and not isinstance(tenure, bool):
        if tenure < MIN_TENURE or tenure > MAX_TENURE:
            return result(
                "DISQUALIFIED",
                "DISQUALIFY",
                "The requested tenure must be between 3 and 15 years.",
                end_call=True,
            )

    # 3. Handle an amount exceeding the offer limit.
    loan_amount = eligibility.get("loan_amount")

    if (
        isinstance(loan_amount, (int, float))
        and not isinstance(loan_amount, bool)
        and loan_amount > MAX_LOAN_AMOUNT
        and flow.get("max_amount_accepted") is not True
    ):
        result_state["flow"]["max_amount_offer_pending"] = True
        return result(
            "PENDING",
            "ASK_TO_PROCEED_WITH_75_LAKH",
            "The requested amount exceeds the ₹75 lakh offer limit.",
        )

    # 4. Find the next unanswered field.
    missing_field = get_missing_field(eligibility)

    if missing_field is not None:
        action = get_next_question(missing_field)
        result_state["flow"]["current_question"] = missing_field

        return result(
            "PENDING",
            action,
            f"Waiting for the required field: {missing_field}.",
        )

    # 5. Validate completed categorical answers.
    valid_values = {
        "property_type": {"RESIDENTIAL", "COMMERCIAL", "INDUSTRIAL"},
        "ownership_status": {"SOLE", "JOINT"},
        "documents_available": {"YES", "AVAILABLE", "TRUE", True},
        "occupation": {"SALARIED", "SELF_EMPLOYED"},
        "income_mode": {"BANK"},
    }

    for field, allowed_values in valid_values.items():
        value = normalize_value(eligibility.get(field))

        if value not in allowed_values:
            return result(
                "NEEDS_CLARIFICATION",
                get_next_question(field),
                f"The answer for {field} is missing or not recognized.",
            )

    loan_amount = eligibility.get("loan_amount")
    market_value = eligibility.get("market_value")

    if (
        not isinstance(loan_amount, (int, float))
        or isinstance(loan_amount, bool)
        or loan_amount <= 0
    ):
        return result(
            "NEEDS_CLARIFICATION",
            "ASK_LOAN_AMOUNT",
            "Loan amount must be a positive number in rupees.",
        )

    if (
        not isinstance(market_value, (int, float))
        or isinstance(market_value, bool)
        or market_value <= 0
    ):
        return result(
            "NEEDS_CLARIFICATION",
            "ASK_MARKET_VALUE",
            "Market value must be a positive number in rupees.",
        )

    if (
        not isinstance(tenure, (int, float))
        or isinstance(tenure, bool)
        or not float(tenure).is_integer()
    ):
        return result(
            "NEEDS_CLARIFICATION",
            "ASK_TENURE",
            "Tenure must be provided as a whole number of years.",
        )

    # 6. All fields are present and valid, with no disqualifying rule.
    result_state["flow"]["current_question"] = None

    return result(
        "QUALIFIED",
        "QUALIFIED_FOR_HANDOFF",
        "All required preliminary eligibility checks passed.",
    )

def confirm_max_amount(state, accepted):
    """Handle the customer's response to the ₹75 lakh offer."""
    result_state = deepcopy(state)
    flow = result_state["flow"]
    eligibility = result_state["eligibility"]

    if not flow.get("max_amount_offer_pending"):
        return {
            "updated_state": result_state,
            "decision": result_state["decision"].copy(),
            "next_action": "NO_PENDING_MAX_AMOUNT_CONFIRMATION",
        }

    if accepted:
        eligibility["loan_amount"] = MAX_LOAN_AMOUNT
        flow["max_amount_accepted"] = True
        flow["max_amount_offer_pending"] = False

        return evaluate_state(result_state)

    # The customer has not accepted the maximum amount.
    # Ask for a revised amount instead of treating it as acceptance.
    eligibility["loan_amount"] = None
    flow["max_amount_accepted"] = False
    flow["max_amount_offer_pending"] = False
    flow["current_question"] = "loan_amount"

    result_state["decision"]["status"] = "PENDING"
    result_state["decision"]["reason"] = (
        "Waiting for the customer to provide a revised loan amount."
    )

    return {
        "updated_state": result_state,
        "decision": result_state["decision"].copy(),
        "next_action": "ASK_LOAN_AMOUNT",
    }

    def test_accepting_maximum_updates_amount(self):
        state = eligible_state()
        state["eligibility"]["loan_amount"] = 9_000_000

        offer = evaluate_state(state)
        pending_state = offer["updated_state"]

        result = confirm_max_amount(pending_state, accepted=True)

        self.assertEqual(
            result["updated_state"]["eligibility"]["loan_amount"],
            7_500_000,
        )
        self.assertTrue(
            result["updated_state"]["flow"]["max_amount_accepted"]
        )
        self.assertEqual(
            result["next_action"],
            "QUALIFIED_FOR_HANDOFF",
        )

    def test_declining_maximum_requests_revised_amount(self):
        state = eligible_state()
        state["eligibility"]["loan_amount"] = 9_000_000

        offer = evaluate_state(state)
        pending_state = offer["updated_state"]

        result = confirm_max_amount(pending_state, accepted=False)

        self.assertIsNone(
            result["updated_state"]["eligibility"]["loan_amount"]
        )
        self.assertEqual(result["next_action"], "ASK_LOAN_AMOUNT")