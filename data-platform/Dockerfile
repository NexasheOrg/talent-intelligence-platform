# One-shot loader: generates seed data and loads the gold schema into Postgres.
FROM python:3.12-slim
WORKDIR /app
COPY data-platform/requirements.txt data-platform/requirements.txt
RUN pip install --no-cache-dir -r data-platform/requirements.txt
# Only the pieces the loader needs:
COPY data/seed/generate_seed.py data/seed/generate_seed.py
COPY data-platform/models/gold_schema.sql data-platform/models/gold_schema.sql
COPY data-platform/load_seed.py data-platform/load_seed.py
CMD ["python", "data-platform/load_seed.py"]
