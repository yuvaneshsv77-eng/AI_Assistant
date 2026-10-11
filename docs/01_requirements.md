
---

# 2. `docs/01_requirements.md`

```markdown
# 01 — Requirements Specification

## 1. Objective

Build an automated AI Voice Agent for Home Credit that contacts existing valued customers, informs them about a pre-approved Loan Against Property (LAP) offer, and performs a preliminary eligibility check.

The AI agent is the first point of contact.

Qualified customers should subsequently be connected with a senior human loan expert.

---

## 2. Customer Offer

The customer should be informed about a special LAP offer of up to:

**₹75,00,000 (75 Lakhs)**

The agent must not promise an exact interest rate.

Exact interest rates will be provided by the senior loan expert.

---

## 3. Conversation Requirements

The agent must conduct the conversation in a:

- Natural manner
- Professional manner
- Advisory manner
- Customer-friendly manner

The agent must handle:

- Complete sentences
- Short answers
- Yes/no responses
- Fillers
- Interruptions
- Customer questions
- Diversions
- Information provided out of order
- Customers who are busy

---

## 4. Call Stages

### Stage A — Greeting and Identification

The agent should:

1. Greet the customer.
2. Identify itself using the configured agent name.
3. Verify that it is speaking with the correct customer.

If the customer is busy:

- Acknowledge the situation.
- Ask for a preferred callback time.
- End the current call appropriately.

---

### Stage B — Presenting the Offer

After successful customer verification:

- Explain that the customer has a special/pre-approved LAP offer.
- Explain that the maximum offer amount is ₹75 lakh.
- Ask whether the customer is interested in proceeding.

---

### Stage C — Preliminary Eligibility Check

The agent must collect the following seven checklist items:

1. Property Type
2. Ownership Status
3. Document Availability
4. Loan Amount
5. Occupation & Income Mode
6. Market Value
7. Tenure

Occupation and income mode are treated as two atomic state variables internally.

Therefore, the internal state contains eight eligibility fields.

---

## 5. Sequential Questioning

The agent should normally collect the eligibility information in the required sequence.

However, customers may provide information out of order.

Example:

Customer:

"I have a residential house and I earn through my salary account. I need around ₹40 lakh."

The agent should extract all available information.

The agent must NOT ask again for information that has already been clearly provided.

---

## 6. Eligibility Conditions

### Property Type

Eligible:

- Residential
- Commercial
- Industrial

Not eligible:

- Agricultural

---

### Ownership

Eligible:

- Sole ownership
- Joint ownership

---

### Property Documents

Original property documents must be available for verification.

If original documents are not available, the customer does not qualify for this offer.

---

### Loan Amount

Maximum eligible amount:

₹75 lakh

If the customer requests more than ₹75 lakh:

- Explain that the maximum available under this offer is ₹75 lakh.
- Ask whether the customer wants to proceed with ₹75 lakh.
- Do not immediately reject the customer.

---

### Occupation

Eligible:

- Salaried
- Self-employed

---

### Income Mode

Income must be received through:

- Bank

Cash income is not eligible.

---

### Market Value

The agent must capture the customer's estimated current market value of the property.

No specific market-value eligibility threshold is defined in the assignment.

Therefore, the agent must not invent a market-value rejection rule.

---

### Tenure

Eligible tenure:

3–15 years

Outside this range:

- Below 3 years → not eligible
- Above 15 years → not eligible

---

## 7. Transfer Requirement

If the customer mentions:

- Existing loan on the property
- Wanting to reduce the current EMI
- Loan transfer requirement

The agent should explain that a loan-transfer specialist will contact the customer.

The normal LAP qualification flow should stop.

---

## 8. Immediate Disqualification

If a customer provides a clearly disqualifying answer, the agent should:

1. Acknowledge the information.
2. Politely explain that the customer does not meet the criteria for this specific offer at this time.
3. End the call.

The agent should not continue asking unnecessary eligibility questions after disqualification.

---

## 9. Final Handoff

The customer can proceed to final handoff only when:

- All required eligibility information has been collected.
- No disqualifying condition exists.
- No transfer branch has been triggered.

The agent should then tell the customer that a senior loan expert will contact them shortly.

The senior expert will provide exact interest-rate information and further loan details.

---

## 10. Required System Variables

The system should support:

- company_name
- customer_name
- agent_name
- agent_gender
- current_date
- current_day
- current_time
- additional_context_from_rag
- language_to_speak
- conversation_history
- customer_utterance

The agent must strictly follow the configured agent gender.

---

## 11. Language

The system must support:

- English
- Hindi

The configured `language_to_speak` variable determines the language used by the agent.

---

## 12. Accuracy Requirements

The agent must:

- Follow business rules exactly.
- Avoid inventing eligibility criteria.
- Avoid inventing interest rates.
- Avoid skipping eligibility questions.
- Avoid asking questions that have already been answered.
- Handle interruptions correctly.
- Handle information provided in a different order.
- Maintain customer state throughout the conversation.
- Never hand off before all required information is collected.

---

## 13. Handoff Gate

The final handoff is a strict gate.

The agent must NOT transition to final handoff until all required eligibility fields have been answered.

If the customer diverts the conversation before completion, the agent should handle the diversion appropriately and return to the missing eligibility information.

---

## 14. Primary Success Criteria

A successful implementation should:

1. Correctly identify the customer.
2. Present the offer.
3. Collect all eligibility information.
4. Correctly update state.
5. Correctly handle out-of-order information.
6. Correctly identify disqualification.
7. Correctly handle transfer cases.
8. Correctly handle requests above ₹75 lakh.
9. Never skip required questions.
10. Correctly hand off eligible customers.