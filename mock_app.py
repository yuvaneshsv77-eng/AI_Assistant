
"""Offline mock interface for testing LAP decision logic."""

import json

import streamlit as st

from src.decision_engine import initial_state
from src.orchestrator import handle_turn


st.set_page_config(
    page_title="LAP Voice Agent - Mock Test",
    page_icon="🎙️",
    layout="centered",
)

st.title("LAP Voice Agent — Mock Test Mode")

st.warning(
    "Offline testing mode. This interface does not call Gemini "
    "or transcribe audio. Enter structured customer answers to "
    "test the existing business rules."
)

if "mock_state" not in st.session_state:
    st.session_state.mock_state = initial_state()
    st.session_state.mock_state["customer"]["verified"] = True
    st.session_state.mock_history = []

if st.button("Reset test"):
    st.session_state.mock_state = initial_state()
    st.session_state.mock_state["customer"]["verified"] = True
    st.session_state.mock_history = []
    st.rerun()

st.subheader("Enter a simulated customer answer")

st.caption(
    "Enter a JSON object containing the fields you want to test. "
    "Use the same field names and value formats as your schemas."
)

example = {
    "property_type": "RESIDENTIAL",
    "ownership_status": "SOLE",
    "documents_available": True,
    "loan_amount": 5000000,
    "occupation": "SALARIED",
    "income_mode": "BANK",
    "market_value": 10000000,
    "tenure": 10,
}

answer_json = st.text_area(
    "Structured customer answers",
    value=json.dumps(example, indent=2),
    height=300,
)

if st.button("Process customer answers", type="primary"):
    try:
        answers = json.loads(answer_json)

        if not isinstance(answers, dict):
            raise ValueError("Enter a JSON object, not a list or string.")

        result = handle_turn(
            st.session_state.mock_state,
            answers,
        )

        st.session_state.mock_state = result["updated_state"]

        st.session_state.mock_history.append({
            "answers": answers,
            "result": result,
        })

        st.success("Test turn processed.")

        st.subheader("Decision")
        st.write(result["next_action"])

        st.subheader("Agent response")
        st.write(result["spoken_response"])

        st.subheader("Extracted test answers")
        st.json(answers)

        st.subheader("Updated state")
        st.json(result["updated_state"])

        st.subheader("External action")
        st.json(result.get("external_action_required"))

    except Exception as exc:
        st.error(
            "The test input could not be processed. "
            "Check the JSON format, field names, and allowed values."
        )
        st.exception(exc)

if st.session_state.mock_history:
    st.divider()
    st.subheader("Test history")

    for index, turn in enumerate(
        st.session_state.mock_history, start=1
    ):
        with st.expander(f"Test turn {index}"):
            st.write("Input answers")
            st.json(turn["answers"])

            st.write("Action")
            st.write(turn["result"]["next_action"])

            st.write("Response")
            st.write(turn["result"]["spoken_response"])
