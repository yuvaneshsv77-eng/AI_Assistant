
import unittest

from src.answer_extractor import validate_extracted_answers


class AnswerExtractorTests(unittest.TestCase):

    def test_normalizes_property_type(self):
        result = validate_extracted_answers({
            "property_type": "Residential"
        })
        self.assertEqual(result["property_type"], "RESIDENTIAL")

    def test_accepts_boolean_documents_answer(self):
        result = validate_extracted_answers({
            "documents_available": True
        })
        self.assertIs(result["documents_available"], True)

    def test_preserves_unknown_answers_as_none(self):
        result = validate_extracted_answers({
            "property_type": None,
            "tenure": None,
        })
        self.assertIsNone(result["property_type"])
        self.assertIsNone(result["tenure"])

    def test_rejects_unknown_fields(self):
        with self.assertRaises(ValueError):
            validate_extracted_answers({
                "customer_password": "example"
            })

    def test_rejects_invalid_boolean(self):
        with self.assertRaises(ValueError):
            validate_extracted_answers({
                "documents_available": "yes"
            })

    def test_rejects_non_positive_loan_amount(self):
        with self.assertRaises(ValueError):
            validate_extracted_answers({
                "loan_amount": 0
            })

    def test_accepts_json_string(self):
        result = validate_extracted_answers(
            '{"property_type": "commercial", "tenure": 10}'
        )
        self.assertEqual(result["property_type"], "COMMERCIAL")
        self.assertEqual(result["tenure"], 10)

    def test_rejects_invalid_json(self):
        with self.assertRaises(ValueError):
            validate_extracted_answers('{"property_type": ')


if __name__ == "__main__":
    unittest.main()
