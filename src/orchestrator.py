
"""Conversation orchestration for the Home Credit LAP voice agent.

This module connects structured answer processing to a consistent response
for the future voice or chat layer. It does not call an LLM or place calls.
"""

from copy import deepcopy

from src.answer_processor import process_answers


ACTION_MESSAGES = {
    "VERIFY_CUSTOMER": (
        "Before we discuss the offer, could you please confirm "
        "that I am speaking with the intended customer?"
    ),
    "ASK_PROPERTY_TYPE": (
        "What type of property would you like to use: residential, "
        "commercial, industrial, or agricultural?"
    ),
    "ASK_OWNERSHIP": (
        "Is the property solely owned or jointly owned?"
    ),
    "ASK_DOCUMENTS": (
        "Are the original property documents available?"
    ),
    "ASK_LOAN_AMOUNT": (
        "What loan amount would you like to request in rupees?"
    ),
    "ASK_OCCUPATION_AND_INCOME_MODE": (
        "Are you salaried or self-employed, and is your income "
        "received through a bank or in cash?"
    ),
    "ASK_MARKET_VALUE": (
        "What is the approximate current market value of the property "
        "in rupees?"
    ),
    "ASK_TENURE": (
        "What repayment tenure would you prefer, between 3 and 15 years?"
    ),
    "ASK_TO_PROCEED_WITH_75_LAKH": (
        "This offer has a maximum of ₹75 lakh. Would you like to proceed "
        "with ₹75 lakh?"
    ),
    "ASK_CALLBACK_TIME": (
        "What day and time would be convenient for a callback?"
    ),
    "SCHEDULE_CALLBACK": (
        "Thank you for sharing your preferred callback time."
    ),
    "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST": (
        "A loan-transfer specialist can assist you with your existing "
        "loan or EMI-reduction request."
    ),
    "DISQUALIFY": (
        "Thank you for sharing that information. Based on this offer's "
        "eligibility criteria, we cannot proceed with this application "
        "at this time."
    ),
    "QUALIFIED_FOR_HANDOFF": (
        "Thank you. Your information has passed the preliminary checks. "
        "A senior loan expert can discuss the next steps and exact "
        "interest rate with you. This is not final loan approval."
    ),
}


def handle_turn(state, extracted_answers):
    """Process one turn and return updated state, action, and reply.

    `extracted_answers` must be structured data extracted from the latest
    customer utterance. Raw speech-to-text and LLM extraction are separate.
    """
    if not isinstance(state, dict):
        raise TypeError("state must be a dictionary")

    if not isinstance(extracted_answers, dict):
        raise TypeError("extracted_answers must be a dictionary")

    result = process_answers(deepcopy(state), extracted_answers)
    action = result["next_action"]

    response = {
        "updated_state": result["updated_state"],
        "decision": result["decision"],
        "next_action": action,
        "spoken_response": ACTION_MESSAGES.get(
            action,
            "I'm sorry, could you please clarify that?"
        ),
        "external_action_required": action in {
            "SCHEDULE_CALLBACK",
            "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST",
            "QUALIFIED_FOR_HANDOFF",
        },
    }

    return response