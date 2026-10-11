
import unittest

from src.decision_engine import initial_state
from src.orchestrator import handle_turn


class OrchestratorTests(unittest.TestCase):

    def test_unverified_customer_is_asked_to_verify(self):
        result = handle_turn(initial_state(), {})

        self.assertEqual(result["next_action"], "VERIFY_CUSTOMER")
        self.assertTrue(result["spoken_response"])
        self.assertFalse(
            result["updated_state"]["flow"]["handoff_allowed"]
        )

    def test_verified_customer_is_asked_for_missing_field(self):
        state = initial_state()
        state["customer"]["verified"] = True

        result = handle_turn(state, {})

        self.assertEqual(result["next_action"], "ASK_PROPERTY_TYPE")

    def test_transfer_request_returns_specialist_action(self):
        result = handle_turn(
            initial_state(),
            {"transfer_intent": True},
        )

        self.assertEqual(
            result["next_action"],
            "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST",
        )
        self.assertTrue(result["external_action_required"])

    def test_qualified_customer_gets_handoff_message(self):
        state = initial_state()
        state["customer"]["verified"] = True

        answers = {
            "property_type": "RESIDENTIAL",
            "ownership_status": "JOINT",
            "documents_available": True,
            "loan_amount": 5000000,
            "occupation": "SALARIED",
            "income_mode": "BANK",
            "market_value": 8000000,
            "tenure": 10,
        }

        result = handle_turn(state, answers)

        self.assertEqual(
            result["next_action"],
            "QUALIFIED_FOR_HANDOFF",
        )
        self.assertTrue(result["external_action_required"])
        self.assertIn(
            "not final loan approval",
            result["spoken_response"],
        )

    def test_agricultural_property_returns_disqualification(self):
        state = initial_state()
        state["customer"]["verified"] = True

        result = handle_turn(
            state,
            {"property_type": "AGRICULTURAL"},
        )

        self.assertEqual(result["next_action"], "DISQUALIFY")
        self.assertFalse(
            result["updated_state"]["flow"]["handoff_allowed"]
        )


if __name__ == "__main__":
    unittest.main()