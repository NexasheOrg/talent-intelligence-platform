# infra  ·  Owner: Sujith (pairs under Praveen)

Cloud infrastructure-as-code and the connectors that pull data from source systems.

- `terraform/` - provision storage (ADLS/S3), warehouse, compute, registries
- `connectors/` - source connectors / ingestion functions (HRMS, ATS, timesheet, CRM, CSV)

**Stack:** Terraform, Docker, cloud functions (Azure Functions / AWS Lambda), scheduling.
Start with a CSV/API connector against seed data; grow toward the Azure target in the roadmap.
