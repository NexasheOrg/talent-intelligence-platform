---
id: OPS-05
title: "devops: Terraform skeleton for the cloud target"
module: devops
labels: [devops, stretch]
difficulty: stretch
estimate: 3-4 days
depends_on: [OPS-04]
---

## Why this matters

`infra/terraform/` has been an empty folder since day one, and the architecture doc promises an
Azure target. This is the first honest step: infrastructure described as reviewable code, so the
cloud environment is something the team can read and reason about rather than something one
person clicked into existence.

**Plan only.** Nothing here should apply to a real subscription without the lead's explicit
say-so, and this task does not include doing so.

## What "done" looks like

- [ ] Terraform describing the minimum viable target: a resource group, a container registry, a
      Postgres instance, and somewhere to run containers
- [ ] `terraform init` and `terraform validate` pass
- [ ] `terraform plan` runs in CI on PRs that touch `infra/` - **plan, never apply**
- [ ] Remote state configured, or a clear written note on what's needed before anyone applies
- [ ] Variables for anything environment-specific; no hardcoded names, regions or sizes
- [ ] No secrets in the code or in state instructions
- [ ] `infra/README.md` explains what it creates, the rough monthly cost, and how to destroy it
- [ ] Formatted (`terraform fmt`) and checked in CI

## Where to work

- `infra/terraform/` - `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`
- `infra/README.md`
- `.github/workflows/`

## How to approach it

1. **Pin the provider versions.** Unpinned providers mean the plan changes under you between
   runs, which defeats the point of describing infrastructure as code.
2. Start with the smallest set of resources that could actually run the stack. Resist adding
   monitoring, networking and scaling in the first PR - review quality collapses past a few
   hundred lines.
3. Remote state is not optional for a team, but it is a chicken-and-egg problem (the storage for
   state has to exist first). Either bootstrap it separately or write down exactly what a human
   must create by hand before the first apply.
4. **Cost.** Put the estimated monthly cost in the README. Cloud resources described in code are
   very easy to create and very easy to forget about.

## How to check it

```bash
cd infra/terraform
terraform init -backend=false
terraform validate
terraform fmt -check
terraform plan     # needs credentials; do not apply
```

## Gotchas

- **Do not run `terraform apply`** as part of this task. Creating real, billable infrastructure is
  the lead's decision, not a side effect of a PR.
- Terraform state can contain generated passwords in plain text. Never commit a state file - and
  make sure `.gitignore` covers it before your first `init` (it already lists `*.tfstate`;
  confirm rather than trust).
- If credentials aren't available to you, that's fine and expected - `validate` and `fmt` still
  prove the code is sound, and say in the PR what you couldn't verify.
