---
id: DATA-05
title: "data-platform: ingest an external CSV into bronze"
module: data-platform
labels: [data-platform, stretch]
difficulty: stretch
estimate: 2 days
depends_on: [DATA-02]
---

## Why this matters

Everything so far reads data we generated ourselves, which is always well-formed. Real source
data is not: columns move, encodings vary, someone opens the file in Excel and the dates change
format. A connector that handles a genuinely messy file is the first step toward connecting a
real HRMS or ATS export.

## What "done" looks like

- [ ] A connector that reads a CSV from a folder and lands it in bronze
- [ ] Column mapping lives in config, not in code - a renamed source column is a config change
- [ ] Bad rows are **quarantined with a reason**, not silently dropped and not fatal
- [ ] A run summary: rows read, landed, quarantined
- [ ] Re-running the same file doesn't duplicate data
- [ ] Tests using a deliberately messy fixture: missing columns, blank rows, a bad date, a
      duplicate, a stray BOM
- [ ] Documented in `data-platform/README.md`

## Where to work

- `data-platform/ingestion/csv_connector.py` - new
- `data-platform/ingestion/mappings/` - config
- `data-platform/tests/fixtures/` - the messy CSV
- `data-platform/tests/test_csv_connector.py`

## How to approach it

1. **Write the messy fixture first.** Put every problem you can think of into a ten-row file.
   It's much easier to build against a known-bad file than to imagine failure modes later.
2. Silent drops are the enemy. Every rejected row goes somewhere with the reason attached -
   without that, "we're missing 200 placements" is unanswerable.
3. Encoding: files from Windows often arrive as UTF-8 with a BOM or as cp1252. Handle both, and
   test both.
4. Idempotency needs a stable identity per row - a natural key, or a hash of the content. Decide
   which and say why.

## How to check it

```bash
python -m pytest data-platform/tests
python data-platform/quality/checks.py
```

Run the connector twice on the same file and confirm the row counts don't change.

## Gotchas

- **Never commit real data**, and never commit a file that looks like real data. The fixture is
  obviously synthetic, ten rows, made-up names.
- Don't try to fix bad rows automatically. Quarantine them and let a human decide. Guessing what
  a malformed row meant is how silent corruption gets in.
