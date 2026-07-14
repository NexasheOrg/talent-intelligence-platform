# api  ·  Owner: Amulya

Backend API that serves the gold layer to the web app, with auth + RBAC. Owns the repo's
CI/CD pipeline.

- `src/` - FastAPI (Python) service, endpoints, RBAC, request/response contracts

**Reads only the gold layer** - never bronze/silver. Roles: recruiter / delivery manager /
exec each see a different slice. Also proxies the ML scoring endpoint to the web app.
Keeping the API in Python means the whole backend (API + ML + AI) is one language and deploys
together. **Stack:** FastAPI, Python, Docker, GitHub Actions.
