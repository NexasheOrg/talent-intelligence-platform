# Security Policy

## Reporting a vulnerability
Please report suspected vulnerabilities privately to a maintainer rather than opening a public
issue. Include steps to reproduce and the potential impact.

## Handling data
- No real or customer data belongs in this repository - only the synthetic seed generator.
- Secrets (API keys, connection strings) go in environment variables or a secrets manager,
  never in code or config committed to git.
- The AI assistant runs read-only against an allow-listed set of gold tables and never has
  write access. Keep it that way.
