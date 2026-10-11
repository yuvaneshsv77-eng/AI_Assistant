
---

# 9. `docs/08_integration_contract.md`

```markdown
# 08 — Integration Contract

## 1. Purpose

This document defines how future modules communicate with the qualification engine.

The goal is to allow the voice platform, RAG system, state manager, and LLM to work together without rewriting the core business logic.

---

# 2. Input

The system should receive:

```text
customer_utterance
conversation_history
customer_state
additional_context_from_rag
system_variables