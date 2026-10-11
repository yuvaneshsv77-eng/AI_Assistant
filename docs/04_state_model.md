
---

# 5. `docs/04_state_model.md`

```markdown
# 04 — State Model

## 1. Purpose

The state model stores everything the agent knows about the current customer and conversation.

The model prevents:

- Repeated questions
- Skipped questions
- Incorrect qualification
- Incorrect handoff
- Loss of information during interruptions

---

# 2. Customer State

```text
customer.name
customer.verified