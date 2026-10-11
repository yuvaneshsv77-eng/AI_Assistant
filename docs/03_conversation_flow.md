
---

# 4. `docs/03_conversation_flow.md`

```markdown
# 03 — Conversation Flow

## High-Level Flow

```text
START
  ↓
Greeting
  ↓
Customer Verification
  ↓
Is Customer Busy?
  ├── YES → Ask Callback Time → END
  └── NO
       ↓
Present LAP Offer
       ↓
Existing Loan / EMI Reduction?
  ├── YES → Loan Transfer Specialist → END
  └── NO
       ↓
Eligibility Questions
       ↓
Capture Customer Information
       ↓
Apply Business Rules
       ↓
Disqualified?
  ├── YES → Explain → END
  └── NO
       ↓
All Required Fields Complete?
  ├── NO → Ask Missing Question
  └── YES
       ↓
Qualified
       ↓
Senior Loan Expert
       ↓
END