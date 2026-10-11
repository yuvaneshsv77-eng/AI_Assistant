
"""Transcribe customer audio using the configured Gemini model."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def transcribe_audio(audio_bytes, mime_type="audio/wav"):
    """Convert recorded customer speech into a transcript."""

    if not audio_bytes:
        raise ValueError("The audio recording is empty.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your project .env file."
        )

    client = genai.Client(api_key=api_key)

    prompt = """
    Transcribe the customer audio accurately into written words.
    The conversation concerns a Home Credit Loan Against Property offer.

    Preserve the customer's meaning, corrections, negations, and numbers.
    Recognize Indian financial expressions such as lakh and crore.
    Do not answer the customer or make an eligibility decision.
    Return only the transcript. If speech is not understandable,
    say that the audio could not be understood.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type,
            ),
            prompt,
        ],
    )

    transcript = (response.text or "").strip()

    if not transcript:
        raise RuntimeError("Gemini did not return a transcript.")

    if transcript.lower() in {
        "the audio could not be understood.",
        "the audio could not be understood",
    }:
        raise RuntimeError(
            "The audio was not clear enough. Please record it again."
        )

    return transcript
