# 02 — Business Rules

## 1. Offer Rule

The LAP offer is available up to:

**₹75,00,000**

The agent must never represent an amount greater than ₹75 lakh as available under this offer.

---

# 2. Eligibility Rules

| Field | Eligible Values | Disqualifying Condition |
|---|---|---|
| Property Type | Residential, Commercial, Industrial | Agricultural |
| Ownership | Sole, Joint | None |
| Original Documents | Available | Not available |
| Loan Amount | ≤ ₹75 lakh | > ₹75 lakh requires special handling |
| Occupation | Salaried, Self-employed | None specified |
| Income Mode | Bank | Cash |
| Market Value | Capture value | No threshold specified |
| Tenure | 3–15 years | <3 or >15 years |

---

# 3. Property Type Rule

```text
IF property_type = RESIDENTIAL
    → Eligible

IF property_type = COMMERCIAL
    → Eligible

IF property_type = INDUSTRIAL
    → Eligible

IF property_type = AGRICULTURAL
    → DISQUALIFY