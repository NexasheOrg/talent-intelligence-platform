---
id: AI-05
title: "ai-assistant: answer policy questions from documents"
module: ai-assistant
labels: [ai-assistant, stretch]
difficulty: stretch
estimate: 3-4 days
depends_on: [AI-02]
---

## Why this matters

"How many consultants are on the bench?" is a database question. "What's our notice-period
policy?" is a *document* question, and no amount of SQL will answer it. RAG - retrieval-augmented
generation - covers the second kind: find the relevant passage, then let the model answer from
it.

## What "done" looks like

- [ ] Documents (markdown or PDF) can be indexed from a folder
- [ ] A question routes to **either** SQL or documents, and the answer says which it used
- [ ] Document answers **quote the source passage and name the file**
- [ ] "Not in any document I have" is a valid, common answer
- [ ] Document guardrails of its own: only the configured folder, no path traversal, size limits
- [ ] Sample synthetic policy documents committed as fixtures
- [ ] Tests: routing picks the right path, a passage is retrieved, an unknown question is refused
- [ ] Documented in the README, including what it can't do

## Where to work

- `ai-assistant/assistant/rag.py` - new
- `ai-assistant/assistant/service.py` - routing
- `ai-assistant/docs/` - synthetic fixture documents
- `ai-assistant/tests/test_rag.py`

## How to approach it

1. **Start with retrieval, not generation.** Get "find the right paragraph" working and eyeball
   the results. If retrieval is wrong, no model can save the answer - it will just paraphrase the
   wrong paragraph fluently.
2. Keep the first version simple. Chunk on headings, embed, cosine similarity. A vector database
   is a scaling decision, not a starting point, and this corpus is tiny.
3. **Always cite.** A policy answer without the passage it came from is unverifiable, and policy
   is exactly where being confidently wrong causes real damage.
4. Route on the question. A cheap keyword rule is fine to start; say in the PR how it fails.

## How to check it

```bash
python -m pytest ai-assistant/tests
```

Ask: a policy question that's answerable; a policy question that isn't; and a metric question -
which must still go to SQL, not to the documents.

## Gotchas

- **Never index real HR documents, contracts or SOWs.** Fixtures are synthetic, obviously fake,
  and committed deliberately. Real policy documents contain personal data and commercial terms.
- Document content is untrusted input to the model, same as the question. A document containing
  "ignore your instructions" must not change behaviour - the SQL guardrails still apply to
  anything that comes back as a query.
- RAG confidently answering from an irrelevant passage is the failure mode here. Set a similarity
  floor and return "not found" below it.
