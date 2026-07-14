# api  ·  Owner: Amulya

Backend API that serves the gold layer to the web app, with auth + RBAC. Owns the repo's
CI/CD pipeline.

- `src/` — API service (Spring Boot or Node), endpoints, RBAC, request/response contracts

**Reads only the gold layer** — never bronze/silver. Roles: recruiter / delivery manager /
exec each see a different slice. Also proxies the ML scoring endpoint to the web app.
**Stack:** Spring Boot (or Node) · Docker · GitHub Actions.
