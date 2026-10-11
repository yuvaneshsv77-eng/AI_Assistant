
"""Merge extracted customer answers and evaluate the LAP workflow."""

from copy import deepcopy

from src.decision_engine import (
    evaluate_state,
    initial_state,
    confirm_max_amount,
)

ELIGIBILITY_FIELDS = {
    "property_type",
    "ownership_status",
    "documents_available",
    "loan_amount",
    "occupation",
    "income_mode",
    "market_value",
    "tenure",
}


def process_answers(state, answers):
    """Merge extracted answers into state and return the next action.

    `answers` must contain already-extracted structured data.
    This function does not call an LLM or interpret raw customer speech.
    """
    updated = deepcopy(state)
    customer = updated["customer"]
    eligibility = updated["eligibility"]
    flow = updated["flow"]

    # Transfer requests take priority over normal qualification.
    if answers.get("transfer_intent") is True:
        flow["transfer_intent"] = True
        return evaluate_state(updated)

    # Handle busy/callback requests before eligibility questions.
    if answers.get("busy") is True:
        customer["busy"] = True
        customer["callback_requested"] = (
            answers.get("callback_requested") is True
        )
        customer["callback_time"] = answers.get("callback_time")
        flow["call_status"] = "COMPLETED"
        updated["decision"]["status"] = "CALLBACK_REQUIRED"
        updated["decision"]["reason"] = "Customer is busy."
        return {
            "updated_state": updated,
            "decision": updated["decision"].copy(),
            "next_action": "SCHEDULE_CALLBACK"
            if customer["callback_requested"]
            else "ASK_CALLBACK_TIME",
        }

    # Apply verification details if provided.
    if answers.get("customer_name") is not None:
        customer["name"] = answers["customer_name"]

    if answers.get("verified") is True:
        customer["verified"] = True

    # Merge only fields explicitly provided by the extractor.
    for field in ELIGIBILITY_FIELDS:
        if field in answers and answers[field] is not None:
            eligibility[field] = answers[field]

    # Handle acceptance or rejection of the ₹75 lakh maximum.
    if flow.get("max_amount_offer_pending"):
        accepted = answers.get("max_amount_accepted")

        if accepted is not None:
            return confirm_max_amount(updated, accepted)

    # If the maximum confirmation is received with the initial amount,
    # let the decision engine create the pending confirmation first.
    result = evaluate_state(updated)

    if (
    result["next_action"] == "ASK_TO_PROCEED_WITH_75_LAKH"
    and answers.get("max_amount_accepted") is True):
        
     return confirm_max_amount(result["updated_state"], True)

    # Verification must happen before qualification.
    if not customer["verified"]:
        result["next_action"] = "VERIFY_CUSTOMER"
        result["updated_state"]["flow"]["stage"] = "VERIFICATION"
        result["updated_state"]["flow"]["handoff_allowed"] = False
        return result

    result["updated_state"]["flow"]["stage"] = (
        "COMPLETED"
        if result["decision"]["status"] in {
            "DISQUALIFIED",
            "TRANSFER_REQUIRED",
            "QUALIFIED",
        }
        else "ELIGIBILITY"
    )

    return result