"""The "ask your data" service.

    uvicorn assistant.service:app --app-dir ai-assistant --port 8100

    curl -X POST localhost:8100/api/assistant/ask \
         -H 'content-type: application/json' \
         -d '{"question": "how many consultants are on the bench?"}'

Every answer comes back with the SQL that produced it. That isn't a debug feature - it's the
product. An answer nobody can check is worse than no answer, because people act on it.
"""

import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .guardrails import Unsafe, validate
from .nl2sql import CannotAnswer, examples, translate

ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(
    title="TIP AI assistant",
    version="0.1.0",
    description="Natural-language questions over the gold layer. Read-only, table allow-listed.",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Question(BaseModel):
    question: str = Field(description="A plain-English question about the gold layer")


class Answer(BaseModel):
    question: str
    answer: str
    sql: str | None = Field(description="The query that produced the answer - always shown")
    rows: list[dict]
    intent: str | None = None
    ok: bool


def _connect():
    """Open a read-only connection. Mirrors data-platform/db.py - see the note there."""
    url = os.environ.get("DATABASE_URL") or f"sqlite:///{ROOT / 'data' / 'local' / 'tip.db'}"
    if url.startswith("postgres"):
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(url)
        # Belt and braces: the guardrails already reject writes, and this stops one anyway.
        conn.set_session(readonly=True)
        return conn, True

    path = Path(url.split("sqlite:///", 1)[1])
    path = path if path.is_absolute() else ROOT / path
    # SQLite opened via a file: URI with mode=ro genuinely cannot write.
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn, False


def run_query(sql, params):
    conn, is_postgres = _connect()
    try:
        if is_postgres:
            import psycopg2.extras

            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql.replace("?", "%s"), tuple(params))
            return [dict(row) for row in cur.fetchall()]

        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok", "answerable_questions": len(examples())}


@app.get("/api/assistant/examples")
def list_examples():
    """What the assistant can answer today. The web app shows these as suggestions."""
    return {"examples": examples()}


@app.post("/api/assistant/ask", response_model=Answer)
def ask(body: Question):
    """Answer a question, or say plainly that it can't be answered.

    Note what this never does: guess. If no intent matches, it returns `ok: false` and lists
    what it *can* answer. Making something up here would be the worst possible failure mode.
    """
    try:
        sql, params, template, intent_name = translate(body.question)
    except CannotAnswer as reason:
        return Answer(question=body.question, answer=str(reason), sql=None, rows=[], ok=False)

    try:
        safe_sql = validate(sql)
    except Unsafe as reason:
        # Reaching here means a bug in nl2sql, not a user problem - but it's still refused.
        return Answer(
            question=body.question,
            answer=f"That query was refused: {reason}",
            sql=sql,
            rows=[],
            intent=intent_name,
            ok=False,
        )

    rows = run_query(safe_sql, params)

    if rows and "value" in rows[0]:
        answer = template.format(value=rows[0]["value"])
    elif rows:
        answer = template
    else:
        answer = "No rows matched that question."

    return Answer(
        question=body.question,
        answer=answer,
        sql=safe_sql,
        rows=rows,
        intent=intent_name,
        ok=True,
    )
