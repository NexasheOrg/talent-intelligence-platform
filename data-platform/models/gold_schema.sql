-- Gold star schema (M0). Columns match the seed generator's output exactly.
-- Idempotent: safe to re-run. This is the shared contract downstream layers read.

DROP TABLE IF EXISTS fact_timesheets, fact_bench, fact_placements, fact_pipeline,
                     dim_job, dim_client, dim_consultant CASCADE;

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
