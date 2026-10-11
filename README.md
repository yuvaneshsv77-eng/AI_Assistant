# SalesAgents AI — Home Credit LAP Qualification Voice Agent

## Project Overview

This project implements the foundation for an AI Voice Agent designed for Home Credit.

The AI Voice Agent will contact existing valued customers, inform them about a pre-approved Loan Against Property (LAP) offer, perform a preliminary eligibility check, and qualify the customer before handing the lead over to a senior human loan expert.

The agent must conduct the conversation naturally, professionally, and in an advisory manner.

---

## Use Case

### Company
Home Credit

### Product
Loan Against Property (LAP)

### Maximum Offer
₹75,00,000 (75 Lakhs)

### Primary Objective

The AI agent should:

1. Verify the correct customer.
2. Handle customers who are busy and request a callback time.
3. Explain the pre-approved LAP offer.
4. Identify whether the customer has an existing loan / wants EMI reduction.
5. Collect all required eligibility information.
6. Handle information provided out of order.
7. Apply eligibility rules accurately.
8. Immediately stop when a disqualifying condition is identified.
9. Handle loan requests above ₹75 lakh correctly.
10. Transfer qualified customers to a senior loan expert.
11. Never provide unsupported exact interest rates.

---

## Project Architecture

```text
Module 1 — Business Requirements
        ↓
Module 2 — State + Decision Engine
        ↓
Module 3 — System Prompt
        ↓
Module 4 — Voice / STT / TTS
        ↓
Module 5 — RAG
        ↓
Module 6 — Testing / Evaluation
        ↓
Module 7 — Final Integration