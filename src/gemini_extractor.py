
"""Gemini-powered structured answer extraction for the LAP voice agent.

Gemini extracts facts from the latest customer utterance.
The answer validator and Python decision engine remain authoritative.
"""

import json
import os

from dotenv import load_dotenv
from google import genai

from src.answer_extractor import validate_extracted_answers

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

EXTRACTION_INSTRUCTIONS = """
You extract structured facts for a Home Credit Loan Against Property
(LAP) customer conversation.

Return only a valid JSON object. Do not provide explanations or markdown.

Extract only facts supported by the latest customer utterance.
Use conversation history and workflow state only to interpret short replies,
such as "yes", "no", or a correction to an earlier answer.

Do not invent missing answers. Omit fields not established by the latest
utterance. Use the following exact field names and values:

customer_name: string
verified: boolean
busy: boolean
callback_requested: boolean
callback_time: string
transfer_intent: boolean
property_type: RESIDENTIAL, COMMERCIAL, INDUSTRIAL, or AGRICULTURAL
ownership_status: SOLE or JOINT
documents_available: boolean
loan_amount: number in Indian rupees
max_amount_accepted: boolean
occupation: SALARIED or SELF_EMPLOYED
income_mode: BANK or CASH
market_value: number in Indian rupees
tenure: integer number of years

Important rules:
- Do not infer that a customer is verified merely because they answer a
  property question. Set verified only when the utterance clearly confirms
  the requested identity verification.
- "My income comes to my bank account" means income_mode BANK.
- "I receive income in cash" means income_mode CASH.
- If the customer says they have an existing property loan, want to transfer
  it, or want to reduce its EMI by transferring it, set transfer_intent true.
- Set busy true when the customer says they cannot talk now or are busy.
- Set callback_requested true only when a callback is requested.
- For "yes" or "no" to a pending ₹75 lakh offer, use the supplied workflow
  state and conversation history to determine max_amount_accepted.
- If the answer is ambiguous, omit the uncertain field.
- Never decide eligibility, approve a loan, or invent an interest rate.
- Amounts such as "50 lakh" mean 5000000 rupees.
- Amounts such as "75 lakhs" mean 7500000 rupees.
- Market value must be expressed in rupees.
"""


def extract_answers(
    customer_utterance,
    conversation_history=None,
    current_state=None,
    client=None,
):
    """Extract and validate facts from one customer utterance.

    `client` is injectable for unit tests. In normal use, the Gemini client
    is created from GEMINI_API_KEY in the environment or .env file.
    """
    if not isinstance(customer_utterance, str) or not customer_utterance.strip():
        raise ValueError("customer_utterance must be a non-empty string.")

    if client is None:
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Configure it in your local .env file."
            )
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    context = {
        "conversation_history": conversation_history or [],
        "current_workflow_state": current_state or {},
        "latest_customer_utterance": customer_utterance.strip(),
    }

    prompt = (
        EXTRACTION_INSTRUCTIONS
        + "\n\nExtract facts from this input:\n"
        + json.dumps(context, ensure_ascii=False, default=str)
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0,
        },
    )

    response_text = getattr(response, "text", None)

    if not response_text:
        raise RuntimeError("Gemini returned an empty response.")

    # The validator rejects malformed JSON, unsupported fields, and
    # invalid values before they reach the decision engine.
    return validate_extracted_answers(response_text)
