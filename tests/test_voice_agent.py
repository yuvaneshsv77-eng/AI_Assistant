
import unittest
from unittest.mock import patch

from src.decision_engine import initial_state
from src.voice_agent import handle_customer_utterance


class VoiceAgentTests(unittest.TestCase):

    @patch("src.voice_agent.extract_answers")
    def test_extracted_answers_reach_orchestrator(self, mock_extract):
        mock_extract.return_value = {
            "property_type": "RESIDENTIAL"
        }

        state = initial_state()
        state["customer"]["verified"] = True

        result = handle_customer_utterance(
            state,
            "I have a residential property.",
            conversation_history=[],
        )

        self.assertEqual(
            result["extracted_answers"]["property_type"],
            "RESIDENTIAL",
        )
        self.assertEqual(result["next_action"], "ASK_OWNERSHIP")
        mock_extract.assert_called_once()

    @patch("src.voice_agent.extract_answers")
    def test_agricultural_property_disqualifies(self, mock_extract):
        mock_extract.return_value = {
            "property_type": "AGRICULTURAL"
        }

        state = initial_state()
        state["customer"]["verified"] = True

        result = handle_customer_utterance(
            state,
            "The property is agricultural.",
        )

        self.assertEqual(result["next_action"], "DISQUALIFY")
        self.assertFalse(
            result["updated_state"]["flow"]["handoff_allowed"]
        )


if __name__ == "__main__":
    unittest.main()
