
"""Browser-based voice interface for the LAP customer agent."""

import hashlib
from io import BytesIO

import streamlit as st
from gtts import gTTS

from src.audio_transcriber import transcribe_audio
from src.decision_engine import initial_state
from src.voice_agent import handle_customer_utterance


st.set_page_config(
    page_title="LAP Voice Agent",
    page_icon="🎙️",
    layout="centered",
)

TERMINAL_ACTIONS = {
    "DISQUALIFY",
    "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST",
    "HANDOFF_TRANSFER_SPECIALIST",
    "QUALIFIED_FOR_HANDOFF",
}


def reset_conversation():
    st.session_state.agent_state = initial_state()
    st.session_state.conversation_history = []
    st.session_state.last_audio_hash = None
    st.session_state.terminal = False


if "agent_state" not in st.session_state:
    reset_conversation()

st.title("🎙️ Loan Against Property Voice Agent")
st.caption("Home Credit LAP pre-qualification demo")

st.info(
    "Allow microphone access when your browser requests it. "
    "Record one customer turn at a time. The system will transcribe "
    "your speech, process the answer, and speak the agent's response."
)

st.warning(
    "Demo only: use fictional customer information. "
    "This application does not approve loans or connect to a live "
    "loan specialist unless a real handoff integration is added."
)

if st.button("Reset conversation"):
    reset_conversation()
    st.rerun()

st.subheader("Conversation")

if not st.session_state.conversation_history:
    st.write(
        "Start by recording the customer's response to the agent's "
        "opening or verification question. The application preserves "
        "conversation state between recording turns."
    )

for turn in st.session_state.conversation_history:
    with st.chat_message("user"):
        st.write(turn["customer"])

    with st.chat_message("assistant"):
        st.write(turn["agent"])

        if turn.get("audio"):
            st.audio(turn["audio"], format="audio/mp3")

if st.session_state.terminal:
    st.success(
        "This conversation has reached a terminal action. "
        "Reset the conversation to start a new test."
    )
else:
    st.subheader("Speak to the agent")

    audio_file = st.audio_input("Record customer speech")

    if audio_file is not None:
        audio_bytes = audio_file.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()

        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash

            try:
                with st.spinner("Transcribing customer audio..."):
                    transcript = transcribe_audio(
                        audio_bytes,
                        mime_type=audio_file.type or "audio/wav",
                    )

                st.write("**Recognized transcript:**")
                st.write(transcript)

                with st.spinner("Processing the customer response..."):
                    result = handle_customer_utterance(
                        state=st.session_state.agent_state,
                        customer_utterance=transcript,
                        conversation_history=(
                            st.session_state.conversation_history
                        ),
                    )

                agent_text = result["spoken_response"]

                # Generate audio for the agent's response.
                audio_buffer = BytesIO()
                gTTS(text=agent_text, lang="en").write_to_fp(audio_buffer)
                response_audio = audio_buffer.getvalue()

                # Save updated state and conversation.
                st.session_state.agent_state = result["updated_state"]

                st.session_state.conversation_history.append({
                    "customer": transcript,
                    "agent": agent_text,
                    "audio": response_audio,
                })

                st.session_state.terminal = (
                    result["next_action"] in TERMINAL_ACTIONS
                )

                st.subheader("Workflow result")
                st.write("**Next action:**", result["next_action"])
                st.write("**Agent response:**", agent_text)

                st.audio(response_audio, format="audio/mp3")

                if st.session_state.terminal:
                    st.success(
                        "The workflow reached a terminal action. "
                        "Review the result before resetting."
                    )

                st.rerun()

            except Exception as exc:
                st.error(
                    "The audio turn could not be completed. "
                    "Check the error below, then try again."
                )
                st.exception(exc)
