---
id: OPS-04
title: "devops: build and publish container images from CI"
module: devops
labels: [devops]
difficulty: core
estimate: 1-2 days
depends_on: [OPS-02]
---

## Why this matters

Every image is currently built on each person's laptop. That means slow first runs for everyone,
and no artefact anywhere that could actually be deployed. Publishing images from CI is the step
between "runs locally" and "could run somewhere else".

## What "done" looks like

- [ ] `api`, `web`, `assistant` and `loader` images build in CI and publish to GitHub Container
      Registry on merge to `main`
- [ ] Tagged with the git SHA **and** `latest` - a SHA tag is the only way to say which code an
      image contains
- [ ] Pull requests **build** the images but do not publish
- [ ] Docker layer caching, so a normal build is a couple of minutes rather than ten
- [ ] The images are reasonably small - check what you're shipping
- [ ] A documented way to run the stack from published images instead of building locally
- [ ] Uses the repository's built-in `GITHUB_TOKEN`, not a hand-made personal token

## Where to work

- `.github/workflows/ci.yml` or a new `publish.yml`
- `docker-compose.prod.yml` - new, pulling images instead of building
- `README.md`

## How to approach it

1. `docker/build-push-action` with `cache-from`/`cache-to: type=gha` handles both the build and
   the caching. Don't hand-roll it.
2. **Publish only from `main`.** A PR from a fork must never be able to push an image - that's a
   supply-chain hole, and the default `pull_request` trigger will hand it to you if you're not
   careful about permissions.
3. Set `permissions: packages: write` on the job, not the whole workflow. Narrow by default.
4. Look at the resulting image sizes. The `web` image should be small - it's nginx and a static
   bundle. If it's hundreds of megabytes, the build stage is leaking into the final image.

## How to check it

Open a PR: images build, nothing publishes. Merge it: images appear in the repository's Packages
tab, tagged with the SHA. Then pull one and run it.

```bash
docker compose -f docker-compose.prod.yml up
```

## Gotchas

- The `web` image bakes in a build-time configuration, so an image built for local use has local
  assumptions in it. Note that limitation - it's the thing that surprises people at deploy time.
- Publishing on every PR is how registries fill with hundreds of dead tags. Main only.
- Don't put secrets in build args. They persist in the image layers and are trivially readable.
