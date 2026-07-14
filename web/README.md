# web  ·  Owners: Laya + Eshwar

The product surface. React SPA with the dashboards and the "ask your data" box.

- `src/` - React + TypeScript app; dashboards, charts, the AI-assistant panel

**Dashboards (MVP):** Utilization & Bench · Placement Funnel · Timesheet/Billing · Client
Health. Talks to `api/` for data, `ml/` for risk scores, `ai-assistant/` for NL queries.
**Stack:** React, TypeScript, Vite, Recharts/D3.

**M0 (built):** a single Utilization & Bench page (`src/App.tsx`) that reads the API and shows
live numbers + a simple bar chart. Runs as part of `docker compose up` (root), on
http://localhost:8080. Next: real charts (Recharts), routing, and the other dashboards.
