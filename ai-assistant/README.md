# ai-assistant  ·  Owners: Eshwar + Laya

The "ask your data" service.

- `src/` - FastAPI service: **NL→SQL** over the gold layer + **RAG** over policy/SOW docs

**Guardrails:** read-only, table-allow-listed (gold only), never write access. NL→SQL answers
metric questions ("bench count by skill last month"); RAG answers document questions ("what's
our notice-period policy?"). Returns the generated SQL + result so users can trust it.
**Stack:** Python, FastAPI, an LLM API, a vector DB for embeddings.
