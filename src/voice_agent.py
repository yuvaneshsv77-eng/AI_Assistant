
"""Entry point connecting Gemini extraction to the LAP workflow."""

from src.gemini_extractor import extract_answers
from src.orchestrator import handle_turn


def handle_customer_utterance(
    state,
    customer_utterance,
    conversation_history=None,
):
    """Process one customer utterance through the complete text workflow."""

    extracted_answers = extract_answers(
        customer_utterance=customer_utterance,
        conversation_history=conversation_history,
        current_state=state,
    )

    result = handle_turn(state, extracted_answers)
    result["extracted_answers"] = extracted_answers

    return result
