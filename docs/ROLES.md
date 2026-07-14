# Team & Ownership

Everyone owns a vertical slice they can demo. The lead keeps the slices fitting together.

## Laya - Lead / Architect (Product owner)
**Owns:** product direction, the gold-schema contract, the AI-layer design, the React app
shell, cross-layer review, roadmap & scope.
**Also builds:** `web/` dashboard shell + the AI-assistant integration, alongside Eshwar.
**Why:** the only team member who spans frontend, API, data pipelines, *and* RAG/LLM - so the
person who can hold the whole system in their head and unblock any layer.

## Praveen - Data Platform (backbone)
**Owns:** [`data-platform/`](../data-platform) - ingestion, medallion transforms (bronze→
silver→gold), the star-schema models, data-quality checks. PySpark + dbt; Azure Databricks/
Synapse for the cloud target.
**Interfaces:** publishes the gold schema everyone downstream consumes.

## Amulya - App Backend & DevOps
**Owns:** [`api/`](../api) - FastAPI (Python) API over the gold layer, auth + RBAC,
request/response contracts, Docker, and the GitHub Actions CI/CD pipeline for the repo.
**Interfaces:** serves the web app; consumes gold + the ML scoring endpoint.

## Eshwar - AI / ML Features
**Owns:** [`ml/`](../ml) attrition-risk / bench-duration model (scikit-learn) and
[`ai-assistant/`](../ai-assistant) NL→SQL + RAG service. Also pairs with Laya on `web/`.
**Why:** his fraud/burnout ML and semantic-search work transfer directly.

## Sujith - Cloud Infra & Connectors
**Owns:** [`infra/`](../infra) - Terraform IaC, source connectors / ingestion functions,
storage, scheduling. Pairs under Praveen.
**Why:** grows real cloud-engineering reps (AWS/Azure) on a production-shaped system.

---

## How we work as a team
- Each person's slice **runs locally from seed data** - no one waits on cloud access.
- The **gold schema is the seam** between Praveen's world and everyone else's. Agree on it
  early; change it only by PR.
- Juniors (Eshwar, Sujith) pair with a senior on their first issue. Laya or Praveen reviews.
- Weekly: demo your slice against seed data. Working software over status updates.
