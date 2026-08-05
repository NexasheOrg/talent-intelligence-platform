# Setting up on Windows

**Read this if you have never run a project like this before.** It assumes no coding
experience and no terminal. Follow it top to bottom; it takes about 45 minutes, most of which
is waiting for downloads.

You do not need to understand the app to get it running. Understanding comes after.

---

## Before you start: two rules that save an afternoon

1. **Don't download the code as a ZIP.** Use GitHub Desktop, as described in step 2. Windows
   marks files that came out of a ZIP as "from the internet" and then refuses to run them,
   which produces a confusing error much later.
2. **Don't put the project inside OneDrive.** If your `Documents` folder syncs to OneDrive
   (most work laptops do), put the project somewhere else - `C:\Projects` is a good choice.
   OneDrive syncs files while the app is using them, and things break in ways that are very
   hard to diagnose.

---

## Step 1 - Install what you need

Install these in order. Each download is a normal Windows installer: run it, click Next, accept
the defaults unless this page says otherwise.

### 1a. GitHub Desktop - gets the code onto your laptop

<https://desktop.github.com>

Sign in with your GitHub account when it asks. If you don't have one yet, create one at
<https://github.com> first, then send your username to your team lead so they can give you
access.

### 1b. VS Code - the editor you'll write code in

<https://code.visualstudio.com>

On the "Select Additional Tasks" screen, tick **"Add to PATH"** if it's offered.

### 1c. Docker Desktop - runs the whole app

<https://www.docker.com/products/docker-desktop>

This is the one that sometimes needs attention:

- If the installer offers **"Use WSL 2 instead of Hyper-V"**, leave it ticked. WSL 2 is a
  Windows component Docker needs; the installer sets it up for you.
- **It will ask you to restart your computer.** Do it. Docker won't work until you have.
- After restarting, **open Docker Desktop once from the Start menu** and leave it running. It
  needs to be running whenever you want to use the app. The whale icon appears near the clock
  when it's ready.

**If Docker won't install**, don't get stuck - skip to
[Running without Docker](RUN-WITHOUT-DOCKER.md) and tell your lead. That path needs Python and
Node.js instead, and it works fine. This happens on locked-down laptops and isn't your fault.
Common causes:

| What you see | What it means |
|---|---|
| "You need admin rights" | Your IT policy blocks installs. Ask IT, or use the no-Docker route. |
| "Virtualization is disabled" / "Enable VT-x" | A BIOS setting is off. IT has to change it - you can't. |
| "WSL 2 installation is incomplete" | Open PowerShell **as administrator** and run `wsl --install`, then restart. |
| Windows 10 Home, very old build | Update Windows first (Settings → Windows Update). |

### 1d. Optional for now - Python and Node.js

You only need these if you're going to edit the backend or the dashboard directly, or if you
can't use Docker. You can come back to this later.

- **Python 3.12+** - <https://www.python.org/downloads>
  On the **first screen of the installer, tick "Add python.exe to PATH"** before clicking
  Install. This one tick causes more problems than anything else in this document.
- **Node.js 20+** - <https://nodejs.org>, choose the **LTS** version.

---

## Step 2 - Get the code

1. Open **GitHub Desktop**.
2. **File → Clone repository**.
3. Choose the **URL** tab and paste:
   `https://github.com/NexasheOrg/talent-intelligence-platform`
4. For **Local path**, pick a folder outside OneDrive - for example `C:\Projects`.
5. Click **Clone**. This takes a few seconds.

You now have a folder like `C:\Projects\talent-intelligence-platform`. Open it in File
Explorer - you'll see files including `START-HERE.bat`.

---

## Step 3 - Check your laptop is ready

Double-click **`CHECK-MY-SETUP.bat`**.

A black window opens and prints a list. It changes nothing on your machine - it only looks
around and tells you what's missing, with the link to install it.

If a blue box says **"Windows protected your PC"**, click **More info → Run anyway**. That
warning appears for any script Windows hasn't seen before.

Fix anything it flags, then run it again until it says you're ready.

---

## Step 4 - Run the app

Make sure **Docker Desktop is open and running**, then double-click **`START-HERE.bat`**.

A black window opens and talks you through what it's doing. **The first run takes 3 to 10
minutes** - it's downloading and building everything. Later runs take a few seconds.

Leave the window open. When it's finished you'll see:

```
  The app is running.

    Dashboard   http://localhost:8080
    API docs    http://localhost:8000/docs
```

Your browser opens automatically at the dashboard.

### What you should see

A dark page titled **Overview**, with real numbers - utilization around 80%, 300 consultants,
some on the bench - and a list of dashboards down the left.

Those numbers are **fake data**, generated on your laptop. There is no real customer data in
this project and there never will be. That's rule one of the whole repo.

Click into **Utilization & Bench**, **Placement Funnel** and **Consultants** to see the
finished pages. **Client Health**, **Timesheet & Billing** and **Ask your data** are marked
`todo` - those are tasks waiting to be built, possibly by you.

### To stop it

Double-click **`STOP.bat`**. Safe to run any time, even if nothing is running.

---

## If something goes wrong

Work down this list. If none of it helps, post the **exact text** from the black window in the
team chat - a screenshot of the error is worth ten minutes of describing it.

**"Docker Desktop is not available"**
Docker isn't installed or isn't running. Open Docker Desktop from the Start menu, wait for the
whale icon near the clock to stop animating, then try again.

**The black window flashes and disappears**
Something failed before the script could print anything. Run `CHECK-MY-SETUP.bat` instead -
it's designed to stay open and tell you what's wrong.

**"Port 8080 is already in use"**
Another program has that port. Usually it's an old copy of this app - `STOP.bat` clears it. If
not, the script tells you which program to close.

**It's been stuck on "Building" for ten minutes**
The first build genuinely is slow, especially on a corporate network. Fifteen minutes is
plausible. Half an hour is not - stop it and ask.

**"failed to solve" / "connection refused" during the build**
Your network blocked the download. Try again; if you're on a corporate VPN, try with it off, or
ask your lead about a proxy.

**The dashboard opens but says "Could not reach the API"**
The dashboard started before the API finished. Wait ten seconds and refresh. If it persists,
run `STOP.bat` then `START-HERE.bat` again.

**Docker says it's out of disk space**
Open Docker Desktop → Troubleshoot → Clean / Purge data, or free up space on your C: drive.
The app needs roughly 5 GB.

**Still stuck after 15 minutes?** Ask in the team chat. Being stuck is normal and expected; it
is not a sign you're behind. Losing a whole afternoon to it silently is the only mistake here.

---

## What's next

- [ONBOARDING.md](ONBOARDING.md) - how to actually work on the code: branches, hot reload,
  pull requests.
- [TASKS.md](TASKS.md) - the list of starter tasks. Find yours.
- Your layer's README: [`api/`](../api), [`web/`](../web),
  [`data-platform/`](../data-platform), [`ml/`](../ml), [`ai-assistant/`](../ai-assistant).
