# Onboarding

Welcome to the team. This gets you from a fresh laptop to running the app locally. Follow it
top to bottom. If you get stuck, ask in the team chat; don't stay blocked.

## 1. What this app is

- A **Talent & Delivery Intelligence Platform**: the analytics brain for a staffing or
  recruitment company.
- It pulls together the numbers that run the business: consultant utilization, time on the
  bench, the submission to placement funnel, timesheets, and client health.
- It has three parts you will hear about a lot:
  - a **data platform** that shapes raw data into clean tables,
  - an **API** that serves those tables,
  - a **web dashboard** plus a predictive model and an "ask your data" AI assistant.
- We build against **synthetic (fake) data** on our laptops, so no real customer data is ever
  needed to develop.
- New here? Also skim the [README](../README.md) and [ARCHITECTURE](ARCHITECTURE.md).

## 2. What to install

Install these in order. Pick the link for your operating system (Windows or Mac).

**Must have**
- **Git**: the version control tool. https://git-scm.com/downloads
- **GitHub Desktop**: a friendly app to clone the repo and make commits without the terminal.
  https://desktop.github.com
- **VS Code**: the code editor we use. https://code.visualstudio.com
- **Docker Desktop**: runs the whole app with one command. https://www.docker.com/products/docker-desktop
  - Windows: it may ask you to enable WSL 2; accept and follow its prompts.
  - After installing, open Docker Desktop once and leave it running.

**Only if you work directly in that layer** (you can skip these at first, Docker covers running the app)
- **Python 3.12+** (data platform, API, ML, AI): https://www.python.org/downloads
- **Node.js 20+** (web dashboard): https://nodejs.org (pick the LTS version)

**Accounts**
- A **GitHub account**. Send your username to the lead so you get added to the
  **NexasheOrg** organization.

## 3. One time setup

- **Sign in to GitHub Desktop**: open it, sign in with your GitHub account.
- **Clone the repo**: in GitHub Desktop, `File > Clone repository > NexasheOrg/talent-intelligence-platform`,
  pick a folder, and clone.
- **Open it in VS Code**: in GitHub Desktop click `Open in Visual Studio Code`.
- **Recommended VS Code extensions** (Extensions panel, search and install):
  - Python (Microsoft)
  - Docker (Microsoft)
  - ESLint and Prettier (for the web app)
- **Check Docker is ready**: Docker Desktop is open and shows "running".

## 4. How to run the app

- Open a terminal in the project folder (in VS Code: `Terminal > New Terminal`).
- Run:
  ```bash
  docker compose up --build
  ```
- The first run takes a few minutes (it downloads and builds things). Later runs are fast.
- When it finishes starting, open:
  - **Dashboard**: http://localhost:8080
  - **API**: http://localhost:8000/api/utilization
- You should see live numbers (utilization, consultants, bench) built from the fake data.
- To stop it: press `Ctrl + C` in that terminal, then run `docker compose down`.

## 5. Working on one layer, with hot reload

Docker runs the whole app, but while you are editing code you want it to reload as you save.
For that, run just the layer you are changing.

### Python layers (`api`, `data-platform`, `ml`, `ai-assistant`)

Python needs a **virtual environment** (a "venv"): a private folder of packages that belongs to
this project only. Create it once, from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt -r requirements-dev.txt
```

On Windows, activate with `.venv\Scripts\activate` instead of the `source` line.

You will know it worked when your terminal prompt starts with `(.venv)`. After that, each new
terminal only needs `source .venv/bin/activate`, and `deactivate` when you are done. The
`.venv/` folder is git-ignored, so it never gets committed.

Now start Postgres in the background and run the API against it:

```bash
docker compose up -d db loader
DATABASE_URL=postgresql://tip:tip@localhost:5433/tip uvicorn main:app --reload --app-dir api --port 8000
```

`--reload` restarts the API every time you save a Python file. That terminal stays busy while
the server runs, so open a second terminal for anything else.

### Web layer (`web`)

```bash
cd web
npm install
npm run dev
```

Vite prints a URL, usually http://localhost:5173. That is a **different port** from the Docker
dashboard on 8080; both read from the same API on port 8000.

## 6. Working on a task

- Full details are in [CONTRIBUTING](../CONTRIBUTING.md). The short version:
  - Pick an **issue** from the repo's Issues tab and assign it to yourself.
  - Make a **branch** for it (in GitHub Desktop: `Current Branch > New Branch`), for example
    `feature/web-funnel-chart`.
  - Make your changes, run the app to check them.
  - **Commit** with a clear message and **push** (GitHub Desktop does both with buttons).
  - Open a **Pull Request** and ask for a review. Keep PRs small.
- Golden rule: never commit real or customer data. Only the fake seed data.

## 7. If something goes wrong

- **`docker: command not found`**: Docker Desktop is not installed or not open. Open it first.
- **Port already in use (8080 or 8000)**: another app is using that port. Find and stop it with
  `lsof -ti:8000 | xargs kill` (swap in the port number), or ask the lead how to change the port.
- **`error: externally-managed-environment`** when installing Python packages: you are
  installing outside a venv, which Macs block on purpose. Create one, see section 5.
- **`command not found: pip`**: activate your venv first (section 5); inside it, plain `pip`
  works. Outside a venv, `pip3` is the name on a Mac.
- **The build seems stuck the first time**: the first build is slow; give it a few minutes.
- **Changes not showing**: stop with `docker compose down`, then `docker compose up --build`
  again.
- Still stuck after 15 minutes? Post the error in the team chat. Don't burn a whole afternoon.

## 8. Where to go next

- Read the README in **your** layer folder: `data-platform/`, `api/`, `web/`, `ml/`,
  `ai-assistant/`, or `infra/`.
- Look at the M0 files already there as your example, then pick up your first issue.
- Ask questions early. That is normal and expected here.
