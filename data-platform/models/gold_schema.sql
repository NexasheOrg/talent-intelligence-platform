-- Gold star schema. Columns match the seed generator's output exactly.
-- Idempotent: safe to re-run. This is the shared contract downstream layers read.
--
-- PORTABLE SQL ONLY. This file runs against Postgres (the Docker stack) *and* SQLite
-- (the no-Docker fallback, see docs/RUN-WITHOUT-DOCKER.md). That means:
--   * one DROP per statement, no `DROP TABLE a, b` and no CASCADE
--   * stick to INTEGER / TEXT / DATE
--   * no Postgres-only types (SERIAL, JSONB), no stored procedures
-- If you need something Postgres-only, raise it in a PR - don't quietly break the SQLite path.

DROP TABLE IF EXISTS fact_timesheets;
DROP TABLE IF EXISTS fact_bench;
DROP TABLE IF EXISTS fact_placements;
DROP TABLE IF EXISTS fact_pipeline;
DROP TABLE IF EXISTS dim_job;
DROP TABLE IF EXISTS dim_client;
DROP TABLE IF EXISTS dim_consultant;

CREATE TABLE dim_consultant (
    consultant_id INTEGER PRIMARY KEY,
    name          TEXT,
    skills        TEXT,
    seniority     TEXT,
    location      TEXT,
    cost_rate     INTEGER,
    hire_date     DATE,
    status        TEXT
);

CREATE TABLE dim_client (
    client_id  INTEGER PRIMARY KEY,
    name       TEXT,
    industry   TEXT,
    tier       TEXT,
    start_date DATE
);

CREATE TABLE dim_job (
    job_id          INTEGER PRIMARY KEY,
    client_id       INTEGER,
    title           TEXT,
    skills_required TEXT,
    open_date       DATE,
    status          TEXT
);

CREATE TABLE fact_pipeline (
    pipeline_id   INTEGER PRIMARY KEY,
    job_id        INTEGER,
    consultant_id INTEGER,
    stage         TEXT,
    stage_date    DATE
);

CREATE TABLE fact_placements (
    placement_id  INTEGER PRIMARY KEY,
    consultant_id INTEGER,
    client_id     INTEGER,
    job_id        INTEGER,
    start_date    DATE,
    end_date      DATE,
    bill_rate     INTEGER,
    margin        INTEGER
);

CREATE TABLE fact_bench (
    bench_id      INTEGER PRIMARY KEY,
    consultant_id INTEGER,
    bench_start   DATE,
    bench_end     DATE,
    days_on_bench INTEGER
);

CREATE TABLE fact_timesheets (
    timesheet_id   INTEGER PRIMARY KEY,
    consultant_id  INTEGER,
    week_ending    DATE,
    hours_billable INTEGER,
    hours_bench    INTEGER
);

-- Indexes on the foreign keys the API joins on most.
CREATE INDEX idx_pipeline_job         ON fact_pipeline (job_id);
CREATE INDEX idx_pipeline_consultant  ON fact_pipeline (consultant_id);
CREATE INDEX idx_placements_client    ON fact_placements (client_id);
CREATE INDEX idx_placements_consultant ON fact_placements (consultant_id);
CREATE INDEX idx_bench_consultant     ON fact_bench (consultant_id);
CREATE INDEX idx_timesheets_consultant ON fact_timesheets (consultant_id);
CREATE INDEX idx_timesheets_week      ON fact_timesheets (week_ending);
CREATE INDEX idx_job_client           ON dim_job (client_id);
