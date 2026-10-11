
from src.decision_engine import initial_state
from src.voice_agent import handle_customer_utterance


def run_scenario(title, utterances):
    print(f"\n{'=' * 55}")
    print(title)
    print("=" * 55)

    state = initial_state()
    state["customer"]["verified"] = True
    history = []

    for utterance in utterances:
        print(f"\nCustomer: {utterance}")

        result = handle_customer_utterance(
            state,
            utterance,
            conversation_history=history,
        )

        state = result["updated_state"]
        history.append({
            "customer": utterance,
            "agent": result["spoken_response"],
        })

        print("Extracted:", result["extracted_answers"])
        print("Next action:", result["next_action"])
        print("Agent:", result["spoken_response"])

        if result["next_action"] in {
            "DISQUALIFY",
            "HANDOFF_TRANSFER_SPECIALIST",
            "QUALIFIED_FOR_HANDOFF",
        }:
            print("\nScenario reached a terminal action.")
            break


if __name__ == "__main__":
    run_scenario(
        "Scenario 1: Agricultural property",
        [
            "My property is agricultural land."
        ],
    )

    run_scenario(
        "Scenario 2: Existing property loan transfer",
        [
            "I already have a loan against my property "
            "and want to transfer it to reduce my EMI."
        ],
    )
