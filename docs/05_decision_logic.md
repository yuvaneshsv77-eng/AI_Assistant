
---

# 6. `docs/05_decision_logic.md`

```markdown
# 05 — Decision Logic

## 1. Purpose

The decision engine determines what the agent should do after every customer utterance.

The system should not simply generate a response.

It must first determine:

1. What information was provided?
2. What changed?
3. Does the customer qualify?
4. Is a special branch required?
5. What should happen next?

---

# 2. Processing Pipeline

```text
Customer Utterance
        ↓
Detect Transfer Intent
        ↓
Extract Eligibility Information
        ↓
Update Customer State
        ↓
Apply Disqualification Rules
        ↓
Apply ₹75L Special Rule
        ↓
Check Missing Fields
        ↓
Determine Next Action
        ↓
Generate Response