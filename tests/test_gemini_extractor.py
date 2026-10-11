
import json
import unittest
from unittest.mock import Mock, patch

from src.gemini_extractor import extract_answers


class GeminiExtractorTests(unittest.TestCase):

    def test_extracts_and_validates_json_response(self):
        fake_response = Mock()
        fake_response.text = json.dumps({
            "property_type": "RESIDENTIAL",
            "ownership_status": "JOINT",
            "documents_available": True,
        })

        fake_client = Mock()
        fake_client.models.generate_content.return_value = fake_response

        result = extract_answers(
            customer_utterance=(
                "It's a residential property, jointly owned, "
                "and the original documents are available."
            ),
            client=fake_client,
        )

        self.assertEqual(result["property_type"], "RESIDENTIAL")
        self.assertEqual(result["ownership_status"], "JOINT")
        self.assertIs(result["documents_available"], True)
        fake_client.models.generate_content.assert_called_once()

    def test_rejects_empty_utterance(self):
        with self.assertRaises(ValueError):
            extract_answers("   ", client=Mock())

    def test_rejects_invalid_model_json(self):
        fake_response = Mock()
        fake_response.text = "This is not JSON"

        fake_client = Mock()
        fake_client.models.generate_content.return_value = fake_response

        with self.assertRaises(ValueError):
            extract_answers("I own a residential property.", client=fake_client)

    def test_rejects_unknown_model_fields(self):
        fake_response = Mock()
        fake_response.text = json.dumps({
            "property_type": "RESIDENTIAL",
            "loan_approved": True,
        })

        fake_client = Mock()
        fake_client.models.generate_content.return_value = fake_response

        with self.assertRaises(ValueError):
            extract_answers("I own a residential property.", client=fake_client)

    def test_missing_api_key_is_reported(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("src.gemini_extractor.genai.Client") as mock_client:
                with self.assertRaises(RuntimeError):
                    extract_answers("I own a residential property.")
                mock_client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
