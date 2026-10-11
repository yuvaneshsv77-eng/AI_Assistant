
import unittest


from src.decision_engine import (
    evaluate_state,
    initial_state,
    confirm_max_amount,
)

def eligible_state():
    """Create a complete, eligible test customer."""
    state = initial_state()

    state["customer"]["name"] = "Test Customer"
    state["customer"]["verified"] = True

    state["eligibility"].update({
        "property_type": "RESIDENTIAL",
        "ownership_status": "SOLE",
        "documents_available": "YES",
        "loan_amount": 5_000_000,
        "occupation": "SALARIED",
        "income_mode": "BANK",
        "market_value": 10_000_000,
        "tenure": 10,
    })

    return state


class DecisionEngineTests(unittest.TestCase):

    def test_eligible_customer(self):
        result = evaluate_state(eligible_state())

        self.assertEqual(
            result["next_action"],
            "QUALIFIED_FOR_HANDOFF",
        )
        self.assertTrue(
            result["updated_state"]["flow"]["handoff_allowed"]
        )

    def test_agricultural_property_disqualifies(self):
        state = eligible_state()
        state["eligibility"]["property_type"] = "AGRICULTURAL"

        result = evaluate_state(state)

        self.assertEqual(result["decision"]["status"], "DISQUALIFIED")
        self.assertEqual(result["next_action"], "DISQUALIFY")
        self.assertFalse(
            result["updated_state"]["flow"]["handoff_allowed"]
        )

    def test_cash_income_disqualifies(self):
        state = eligible_state()
        state["eligibility"]["income_mode"] = "CASH"

        result = evaluate_state(state)

        self.assertEqual(result["decision"]["status"], "DISQUALIFIED")

    def test_missing_documents_disqualify(self):
        state = eligible_state()
        state["eligibility"]["documents_available"] = "NO"

        result = evaluate_state(state)

        self.assertEqual(result["decision"]["status"], "DISQUALIFIED")

    def test_tenure_outside_range_disqualifies(self):
        for tenure in (2, 16):
            with self.subTest(tenure=tenure):
                state = eligible_state()
                state["eligibility"]["tenure"] = tenure

                result = evaluate_state(state)

                self.assertEqual(
                    result["decision"]["status"],
                    "DISQUALIFIED",
                )

    def test_joint_ownership_is_allowed(self):
        state = eligible_state()
        state["eligibility"]["ownership_status"] = "JOINT"

        result = evaluate_state(state)

        self.assertEqual(
            result["next_action"],
            "QUALIFIED_FOR_HANDOFF",
        )

    def test_amount_above_limit_requires_confirmation(self):
        state = eligible_state()
        state["eligibility"]["loan_amount"] = 9_000_000

        result = evaluate_state(state)

        self.assertEqual(
            result["next_action"],
            "ASK_TO_PROCEED_WITH_75_LAKH",
        )
        self.assertEqual(result["decision"]["status"], "PENDING")
        self.assertTrue(
            result["updated_state"]["flow"]["max_amount_offer_pending"]
        )

    def test_existing_loan_triggers_transfer(self):
        state = eligible_state()
        state["flow"]["transfer_intent"] = True

        result = evaluate_state(state)

        self.assertEqual(
            result["next_action"],
            "TRANSFER_TO_LOAN_TRANSFER_SPECIALIST",
        )
        self.assertEqual(
            result["decision"]["status"],
            "TRANSFER_REQUIRED",
        )

    def test_missing_field_is_requested(self):
        state = eligible_state()
        state["eligibility"]["market_value"] = None

        result = evaluate_state(state)

        self.assertEqual(result["next_action"], "ASK_MARKET_VALUE")
        self.assertEqual(result["decision"]["status"], "PENDING")

    def test_market_value_has_no_extra_threshold(self):
        state = eligible_state()
        state["eligibility"]["market_value"] = 1

        result = evaluate_state(state)

        self.assertEqual(
            result["next_action"],
            "QUALIFIED_FOR_HANDOFF",
        )

    def test_original_state_is_not_mutated(self):
        state = eligible_state()
        state["eligibility"]["property_type"] = "AGRICULTURAL"

        original_status = state["decision"]["status"]
        evaluate_state(state)

        self.assertEqual(state["decision"]["status"], original_status)


if __name__ == "__main__":
    unittest.main(verbosity=2)