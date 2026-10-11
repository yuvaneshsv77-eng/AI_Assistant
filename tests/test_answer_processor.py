
import unittest

from src.answer_processor import process_answers
from src.decision_engine import initial_state


class AnswerProcessorTests(unittest.TestCase):

    def test_multiple_answers_are_merged(self):
        state = initial_state()
        state["customer"]["verified"] = True

        result = process_answers(state, {
            "property_type": "RESIDENTIAL",
            "ownership_status": "JOINT",
            "documents_available": True,
            "occupation": "SALARIED",
            "income_mode": "BANK",
        })

        eligibility = result["updated_state"]["eligibility"]

        self.assertEqual(eligibility["property_type"], "RESIDENTIAL")
        self.assertEqual(eligibility["ownership_status"], "JOINT")
        self.assertTrue(eligibility["documents_available"])
        self.assertEqual(eligibility["income_mode"], "BANK")

    def test_transfer_intent_takes_priority(self):
        state = initial_state()

        result = process_answers(state, {
            "transfer_intent": True,
            "property_type": "RESIDENTIAL",
        })

        self.assertEqual(
            result["next_action"],
            "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST",
        )

    def test_busy_customer_gets_callback_action(self):
        state = initial_state()

        result = process_answers(state, {
            "busy": True,
            "callback_requested": True,
            "callback_time": "Tomorrow at 10 AM",
        })

        self.assertEqual(result["next_action"], "SCHEDULE_CALLBACK")
        self.assertEqual(
            result["updated_state"]["customer"]["callback_time"],
            "Tomorrow at 10 AM",
        )

    def test_unverified_customer_is_not_handed_off(self):
        state = initial_state()
        state["eligibility"].update({
            "property_type": "RESIDENTIAL",
            "ownership_status": "SOLE",
            "documents_available": "YES",
            "loan_amount": 5000000,
            "occupation": "SALARIED",
            "income_mode": "BANK",
            "market_value": 8000000,
            "tenure": 10,
        })

        result = process_answers(state, {})

        self.assertEqual(result["next_action"], "VERIFY_CUSTOMER")
        self.assertFalse(result["updated_state"]["flow"]["handoff_allowed"])

    def test_boolean_documents_available_allows_qualification(self):
        state = initial_state()
        state["customer"]["verified"] = True

        answers = {
            "property_type": "RESIDENTIAL",
            "ownership_status": "SOLE",
            "documents_available": True,
            "loan_amount": 5000000,
            "occupation": "SALARIED",
            "income_mode": "BANK",
            "market_value": 8000000,
            "tenure": 10,
        }

        result = process_answers(state, answers)

        self.assertEqual(
            result["next_action"],
            "QUALIFIED_FOR_HANDOFF",
        )

    def test_boolean_documents_unavailable_disqualifies(self):
        state = initial_state()
        state["customer"]["verified"] = True

        result = process_answers(state, {
            "property_type": "RESIDENTIAL",
            "documents_available": False,
        })

        self.assertEqual(result["next_action"], "DISQUALIFY")
        self.assertTrue(
            result["updated_state"]["flow"]["disqualified"]
        )

        
    def test_customer_correction_re_evaluates_eligibility(self):
        state = initial_state()
        state["customer"]["verified"] = True
        state["eligibility"]["property_type"] = "RESIDENTIAL"

        result = process_answers(state, {
            "property_type": "AGRICULTURAL",
        })

        self.assertEqual(result["next_action"], "DISQUALIFY")
        self.assertTrue(
            result["updated_state"]["flow"]["disqualified"]
        )

    def test_disqualification_overrides_other_eligible_answers(self):
        state = initial_state()
        state["customer"]["verified"] = True

        result = process_answers(state, {
            "property_type": "RESIDENTIAL",
            "ownership_status": "JOINT",
            "documents_available": False,
            "loan_amount": 5000000,
            "occupation": "SALARIED",
            "income_mode": "BANK",
            "market_value": 8000000,
            "tenure": 10,
        })

        self.assertEqual(result["next_action"], "DISQUALIFY")
        self.assertEqual(
            result["updated_state"]["decision"]["status"],
            "DISQUALIFIED",
        )

    def test_accepting_maximum_offer_updates_amount(self):
        state = initial_state()
        state["customer"]["verified"] = True
        state["eligibility"]["loan_amount"] = 8000000

        first_result = process_answers(state, {})
        self.assertEqual(
            first_result["next_action"],
            "ASK_TO_PROCEED_WITH_75_LAKH",
        )

        second_result = process_answers(
            first_result["updated_state"],
            {"max_amount_accepted": True},
        )

        self.assertEqual(
            second_result["updated_state"]["eligibility"]["loan_amount"],
            7500000,
        )
        self.assertNotEqual(
            second_result["next_action"],
            "ASK_TO_PROCEED_WITH_75_LAKH",
        )

    def test_declining_maximum_offer_requests_revised_amount(self):
        state = initial_state()
        state["customer"]["verified"] = True
        state["eligibility"]["loan_amount"] = 8000000

        first_result = process_answers(state, {})
        second_result = process_answers(
            first_result["updated_state"],
            {"max_amount_accepted": False},
        )

        self.assertEqual(second_result["next_action"], "ASK_LOAN_AMOUNT")
        self.assertIsNone(
            second_result["updated_state"]["eligibility"]["loan_amount"]
        )


if __name__ == "__main__":
    unittest.main()