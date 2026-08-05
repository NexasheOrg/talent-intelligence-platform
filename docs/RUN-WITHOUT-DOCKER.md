# Running without Docker

**Use this if you can't install Docker Desktop** - locked-down laptop, no admin rights, or
virtualization disabled in the BIOS. This route works fine and you can do every task in
[TASKS.md](TASKS.md) with it. Tell your lead you're on this path so they know.

## What changes

The app normally runs Postgres in a container. Without Docker, it uses **SQLite** instead: a
database that lives in a single file and comes built into Python, so there's nothing extra to
install.

| | Docker route | This route |
|---|---|---|
| Database | Postgres in a container | SQLite file at `data/local/tip.db` |
| Needs installed | Docker Desktop | Python 3.12+ and Node.js 20+ |
| Dashboard | <http://localhost:8080> | <http://localhost:5173> |
| API | <http://localhost:8000> | <http://localhost:8000> |
| Code changes | need a restart | reload automatically as you save |

Same gold schema, same API, same dashboard, same tests. The only thing you can't do is test
something Postgres-specific - and there shouldn't be anything Postgres-specific, because
**every query in this repo has to run on both**. If you find one that doesn't, that's a bug
worth raising.

## What to install

- **Python 3.12+** - <https://www.python.org/downloads>
  On the **first screen of the installer**, tick **"Add python.exe to PATH"**. If you miss it,
  the scripts won't find Python and you'll have to reinstall.
- **Node.js 20+** (LTS) - <https://nodejs.org>

## Running it

Double-click **`START-HERE.bat`** as usual. It notices Docker isn't available, explains why,
and offers this route - answer `y`.

The first run takes a few minutes: it creates a private Python environment, installs packages,
builds the database from the seed generator, and installs the dashboard's packages. After
that it starts in seconds.

Two extra windows open, titled **TIP API** and **TIP dashboard**. Those are the two halves of
the app. Leave them open while you work; their logs are where errors show up.

On macOS or Linux, run `./scripts/start-local.sh` instead.

### Doing it by hand

If you'd rather run the steps yourself, or a script fails and you want to see where:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r api\requirements.txt -r requirements-dev.txt

$env:DATABASE_URL = "sqlite:///data/local/tip.db"
python data-platform\load_seed.py
python -m uvicorn app.main:app --app-dir api --port 8000 --reload
```

Then in a **second** window:

```powershell
cd web
npm install
npm run dev
```

On macOS or Linux the only differences are `source .venv/bin/activate` and
`export DATABASE_URL=sqlite:///data/local/tip.db`.

## Stopping it

Close the two windows, or double-click `STOP.bat`.

## Rebuilding the data

The database is a file. To start over - after changing the seed generator, or if you've made a
mess of the data - delete it and reload:

```powershell
del data\local\tip.db
python data-platform\load_seed.py
```

Nothing is lost by doing this. The data is generated, not precious.

## Known differences to watch for

- **SQLite is relaxed about types.** It will happily store the text `"abc"` in a column
  declared `INTEGER`; Postgres would reject it. So a data bug can pass locally and fail in CI.
  This is why `data-platform/quality/checks.py` exists - run it after changing a transform.
- **No concurrent writers.** Only one process can write at a time. That's fine here: the loader
  writes, and everything else only reads.
- **`COPY` doesn't exist.** The loader uses `INSERT` on this route instead. That's handled in
  `data-platform/load_seed.py` - you don't have to think about it.
