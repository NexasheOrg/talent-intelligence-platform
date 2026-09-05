# Frontend Onboarding: Shravani and Manikanta

Welcome to the TIP frontend team. This document is your guide for the first month. It explains what the application does, how React works (with a link to the official documentation for every concept), how our code is organized and why, how the same patterns are used in large production applications, and exactly which tasks each of you owns.

You are both new to React, and that is completely fine. This codebase was deliberately kept small (it has only four runtime dependencies) so that you can read every line of it. The fastest way to learn React is to read the official documentation at [react.dev](https://react.dev/learn) alongside real code that uses each concept. This document pairs every concept with the file in our repository that demonstrates it.

Before anything else, get the application running on your machine by following [docs/ONBOARDING.md](ONBOARDING.md) (or [WINDOWS-SETUP.md](WINDOWS-SETUP.md) if you are on Windows), and then read [web/README.md](../web/README.md).

---

## 1. What we are building

TIP stands for Talent and Delivery Intelligence. It is a dashboard application for a consulting and staffing company. Since you may be new to this industry, here are the business terms you will see everywhere in the code and the data:

- A **consultant** is an employee of the staffing company who is placed with client companies to do work.
- A consultant is **billable** when they are working on a client project and the client is being charged for their time.
- A consultant is **on the bench** when they are between projects. The company is paying their salary, but no client is paying for their time. Keeping the bench small is one of the main goals of this kind of business.
- **Utilization** is the percentage of consultants who are billable. It is the single most important health number for the company.
- The **placement funnel** describes the stages a candidate moves through before they are placed with a client: submitted, then interview, then offer, then placed. It is called a funnel because the number of people gets smaller at each stage.
- **Attrition** means employees leaving the company. Our machine learning model estimates the risk that a given consultant will leave.

The dashboard answers questions such as: how much of our workforce is billable right now, how are candidates moving through the placement funnel, and which consultants are at risk of leaving.

The platform has five layers. The full picture is in [docs/ARCHITECTURE.md](ARCHITECTURE.md):

```
data-platform/  generates synthetic data and loads it into a Postgres database
api/            a FastAPI service that serves that data as JSON
ml/             the attrition risk model
ai-assistant/   a service that turns plain English questions into SQL
web/            the React dashboard. This is where you work.
```

The frontend never touches the database directly. It only makes HTTP requests to the API, and it always uses relative URLs that start with `/api/`. This is the standard shape of a production frontend. Our application is a **single-page application (SPA)**, which means it is built once into a set of static files (HTML, CSS, and JavaScript), those files are served by a web server (nginx in our case), and all data is fetched from the API afterwards. Very large companies use the same architecture. The difference is that they serve the static files from a **content delivery network (CDN)**, which is a set of servers spread around the world so that every user downloads the files from a server near them. The architecture stays the same as an application grows; only the serving infrastructure changes.

One hard rule, stated in the application's own sidebar: we work with synthetic (artificially generated) data only, and never with real customer records.

---

## 2. React in one page: the mental model

Read [Thinking in React](https://react.dev/learn/thinking-in-react) first. It is the single most useful page in the documentation. The table below lists the core ideas. For each one, it links to the official explanation and points to the file in our repository where you can see it used.

| Concept | What it means | Official docs | Where to see it in our code |
|---|---|---|---|
| **Component** | A JavaScript function that returns a piece of user interface. An application is a tree of components. | [Your First Component](https://react.dev/learn/your-first-component) | `web/src/components/Card.tsx` defines `Card`, `Kpi`, and `Pill`, each about 15 lines long. |
| **JSX** | HTML-like syntax written inside JavaScript. Curly braces embed JavaScript expressions. | [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx) | Any file ending in `.tsx`. |
| **Props** | Read-only inputs that a parent component passes to a child, like function arguments. | [Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component) | `DataState.tsx` receives `loading`, `error`, `empty`, and `onRetry` as props. |
| **State** | A component's memory. When state changes, React renders the component again. | [State: A Component's Memory](https://react.dev/learn/state-a-components-memory) | `Consultants.tsx` keeps the search text, the filters, and the page number in state. |
| **Rendering** | React calls your component function, compares the result with what is on screen, and updates only the parts that changed. | [Render and Commit](https://react.dev/learn/render-and-commit) | This happens automatically. |
| **Keys** | Stable identifiers on list items so React can track each item across renders. | [Rendering Lists](https://react.dev/learn/rendering-lists) | The consultants table uses `key={c.consultant_id}` on each row. |
| **Effects** | Code that synchronizes a component with something outside React, such as a network request or a timer. | [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects) | `web/src/lib/api.ts` fetches data inside `useEffect`. |
| **Controlled inputs** | Form inputs whose current value is stored in React state rather than in the browser. | [Reacting to Input with State](https://react.dev/learn/reacting-to-input-with-state) | The search box in `Consultants.tsx`. |
| **Lifting state up** | When two components need the same state, you move that state into their shared parent. | [Sharing State Between Components](https://react.dev/learn/sharing-state-between-components) | The filter values live in the page component, not inside the filter widgets. |
| **Custom hooks** | Reusable stateful logic extracted into a function whose name starts with `use`. | [Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks) | `useApi` in `lib/api.ts` and `useDebounced` in `lib/useDebounced.ts`. |
| **Purity** | A component must not cause side effects while rendering. Given the same props and state, it must return the same output. | [Keeping Components Pure](https://react.dev/learn/keeping-components-pure) | Every component in `src/`. |

Two warnings that will save you weeks of confusion:

1. **Most `useEffect` calls that beginners write are unnecessary.** If you are computing a value from props or state, compute it directly during render; you do not need an effect for that. Read [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect) before you write your first one. In our codebase, effects appear in exactly two places (`useApi` and `useDebounced`), and page components never write their own.
2. **State updates are asynchronous.** Calling `setCount(count + 1)` does not change `count` on the next line. It schedules a new render with the new value. [State as a Snapshot](https://react.dev/learn/state-as-a-snapshot) explains this.

We write TypeScript rather than plain JavaScript, and every component's props get an explicit type. The official guide is [Using TypeScript](https://react.dev/learn/typescript), and the language itself is documented in the [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html). Almost every production team uses TypeScript, because it turns a whole category of runtime bugs (for example, a page that renders but shows `undefined` for every number) into errors the compiler catches before the code ships.

---

## 3. Our architecture, and the production pattern behind each choice

Everything below lives in the `web/` directory. The structure:

```
web/src/
  main.tsx          the entry point: createRoot plus <BrowserRouter>
  App.tsx           the application shell: the sidebar NAV array and all <Routes>
  styles.css        one global stylesheet, with design tokens defined in :root
  lib/
    api.ts          the ONLY place in the app where fetch() is called
    types.ts        TypeScript types that mirror api/app/models.py
    format.ts       number, date, and percentage formatting functions
    useDebounced.ts a hook that delays a changing value by 300 milliseconds
  components/       reusable building blocks (Card, DataState, ChartCard, charts/)
  pages/            one file per route (Overview, Utilization, Funnel, Consultants)
```

### 3.1 Build tool: Vite

We use [Vite](https://vite.dev/guide/why) as our build tool. During development it starts instantly and applies your edits to the running page without a full reload (this is called hot module replacement). The command `npm run build` first runs the TypeScript compiler to check types (`tsc --noEmit`) and then bundles the application into optimized static files in `dist/`. In production teams this same process is called the build pipeline. Large companies run it inside their continuous integration system with more steps added, such as linting, bundle size limits, and uploading source maps to an error tracking service.

### 3.2 Routing: React Router version 6

Routing is the mechanism that shows a different page for each URL. We use [React Router](https://reactrouter.com/en/main) with `BrowserRouter`, which gives us real URLs such as `/consultants` rather than URLs with a `#` in them. All routes are declared in one place, `App.tsx`, next to a `NAV` array that generates the sidebar. Adding a page takes three steps, which are documented in `web/README.md`: create a file in `pages/`, add a `<Route>`, and add a `NAV` entry.

A production detail worth understanding: if someone bookmarks `/funnel` and refreshes the browser, the web server receives a request for a path that does not exist as a file. Our `web/nginx.conf` contains the line `try_files $uri $uri/ /index.html`, which serves the application shell for every unknown path so that React Router can take over. Forgetting this fallback is the cause of the very common "the page works until I refresh, then I get a 404" bug in SPA deployments.

### 3.3 Data fetching: `useApi`, our small version of React Query

The first rule of this codebase is that **components never call `fetch()` directly**. They call the `useApi<T>(path, params)` hook from `lib/api.ts`, which returns an object with `data`, `error`, `loading`, and `reload`. Because every page goes through this one function, every page handles loading and errors in exactly the same way.

Read `lib/api.ts` from top to bottom. It is about 100 lines, and it teaches three real production problems and their solutions:

- **Race conditions.** If the user types quickly and two requests are in flight at once, the older response might arrive last and overwrite newer data. `useApi` sets a cancellation flag in the effect cleanup function so that a stale response is ignored. This exact bug and its fix are described in the official documentation under [Synchronizing with Effects: fetching data](https://react.dev/learn/synchronizing-with-effects#fetching-data).
- **Error normalization.** Every kind of failure becomes an `ApiError` object that carries an HTTP status code. A network failure (the API is unreachable) becomes status `0` with a readable message.
- **Refetching.** Calling `reload()` increments a counter that the effect depends on, which runs the request again.

Some production terminology: the data that `useApi` manages is called **server state**, meaning data that is owned by the backend and cached temporarily on the client. This is different from **UI state**, such as which tab is open or what is typed in the search box. In most production applications, server state is managed by a dedicated library, usually [TanStack Query, also known as React Query](https://tanstack.com/query/latest/docs/framework/react/overview), or SWR. Those libraries add caching, request deduplication, and background refreshing. Our `useApi` is a 60-line version of the same idea. Learn ours first, because you can read all of it; after that, the React Query documentation will feel familiar.

### 3.4 The API contract: `lib/types.ts` and `api/app/models.py`

The TypeScript types for API responses are written by hand in `lib/types.ts`, and they mirror the Pydantic models that the FastAPI backend uses. There is no code generation, which leads to our second rule:

> **Rule 2: any pull request that changes the shape of an API response must update both `api/app/models.py` and `web/src/lib/types.ts` together.**

While the stack is running, you can see the live, interactive API contract at `http://localhost:8000/docs`. This page is generated from the OpenAPI specification, a machine-readable description of every endpoint. Larger teams generate their TypeScript client code automatically from that specification (for example with the `openapi-typescript` tool) so that the two sides can never drift apart. That would be a good future improvement here, but you should understand the manual version first.

### 3.5 Loading, error, and empty states: `DataState`

Every page wraps its content in `<DataState loading={...} error={...} empty={...}>`. This one component decides what a loading indicator, an error message with a retry button, and a "no results" message look like. Because there is exactly one implementation, the whole application behaves consistently, and a designer can change the behavior in one place. In production organizations this idea grows into a **design system**: a shared library of components with the user experience decisions already built in, so that individual product teams cannot each invent their own error handling.

`Consultants.tsx` shows a refinement worth studying. When the user changes a filter and the data is being fetched again, the page dims the existing rows instead of replacing them with a loading spinner, so the layout never jumps. This pattern is often called stale-while-revalidate, and the name comes from [an HTTP caching directive](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#stale-while-revalidate) that works the same way.

### 3.6 Charts: Recharts with a locked color theme

Charts are built with [Recharts](https://recharts.org/en-US/). All chart colors come from `components/charts/theme.ts`. Those specific color values were tested to make sure people with color vision deficiency can tell the data series apart against our panel background.

> **Rule 3: never write a color value directly in a chart file. Import it from `charts/theme.ts`.**

Every chart is wrapped in a `ChartCard` component, which provides a button that shows the same data as a table. This is an **accessibility** requirement, not decoration: users of screen readers, and users who cannot distinguish the chart colors, get the numbers as text.

### 3.7 Styling: plain CSS with design tokens

We have one global stylesheet, `styles.css`. At the top of it, inside `:root`, are **design tokens**: named CSS variables such as `--bg`, `--panel`, `--accent`, `--good`, `--warn`, `--bad`, and `--radius`. Components refer to these names instead of raw color values. We do not use Tailwind or any CSS-in-JS library; for an application this size, plain CSS keeps the number of things you have to learn small. The tokens are also what will make the light theme (task WEB-05) possible: the work is to change the token values, not the components.

### 3.8 Testing: Vitest and React Testing Library

The command `npm test` runs [Vitest](https://vitest.dev/guide/) together with [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/). The Testing Library [guiding principle](https://testing-library.com/docs/guiding-principles/) is to test what the user actually sees (for example, "the page shows 42 consultants") rather than internal implementation details (for example, "the component's state variable equals 42"). Tests written this way keep passing when you refactor the internals.

Three test files already exist, and each one is a pattern you can copy:

- `lib/format.test.ts` contains plain unit tests of pure functions. Start here.
- `components/DataState.test.tsx` renders a component and makes assertions about its output.
- `pages/Overview.test.tsx` is a full page test. It replaces the global `fetch` function with a fake one (`vi.stubGlobal`) that maps each route to a prepared payload, and renders the page inside `<MemoryRouter>`. Its header comment honestly explains what this approach cannot catch: a mismatch between the real API and our types. The Python tests in `api/tests/` cover that side.

### 3.9 Shipping: Docker, nginx, and continuous integration

`web/Dockerfile` is a two-stage build. The first stage uses a Node image to build the static files; the second stage copies them into an nginx image that serves them. `docker-compose.yml` connects the services: web on port 8080, the API on port 8000, the assistant on port 8100, and Postgres. Continuous integration (the `web` job in [.github/workflows/ci.yml](../.github/workflows/ci.yml)) runs the type check, the tests, and the build on every pull request. **A pull request with failing checks cannot be merged.**

Manikanta, this section connects directly to your cloud and DevOps experience. Because the build output is nothing but static files, scaling the frontend to millions of users means putting `dist/` behind a CDN; the frontend itself has no servers that need scaling. What does need scaling is the API, which runs as multiple copies behind a load balancer. Two techniques to know by name for when the application grows: [code splitting with React.lazy](https://react.dev/reference/react/lazy), which makes users download only the JavaScript for the page they visit, and server-side rendering with a framework such as [Next.js](https://nextjs.org/docs), which matters when search engine visibility or first-load speed become requirements. We need neither yet.

---

## 4. House rules: the pull request checklist

Every pull request, from either of you, must satisfy all of the following:

1. **No `fetch()` outside `lib/api.ts`.** Pages use `useApi`.
2. **No color values written directly in chart files.** Import them from `charts/theme.ts`.
3. **A change to an API response shape updates both `models.py` and `types.ts` in the same pull request.**
4. **Loading, error, and empty states are handled through `DataState`.** A page must never show a blank screen while data loads.
5. **TypeScript strict mode, and no `any`** unless you add a comment explaining why it is unavoidable.
6. **At least one test for new logic.** Copy the closest existing test as a template.
7. **Small pull requests.** One task per pull request, ideally under 400 changed lines. Very large pull requests do not get careful reviews.
8. **Checks are green before you request review.** Run `npm test` and `npm run build` locally first.
9. **You review each other's pull requests.** Reviewing is half of how you will learn. Asking "why is it done this way?" in a review comment is expected and welcome.
10. **Match the style of the code around you**: the same naming, file layout, and comment style as the files you are editing. See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## 5. Learning path for week one (both of you, together)

Work through these steps in order. Plan for about three focused days.

1. **Run the stack.** Follow [ONBOARDING.md](ONBOARDING.md). To confirm it works: open `http://localhost:8080`, click every item in the sidebar, then open `http://localhost:8000/docs` and execute `GET /api/consultants` from that page.
2. **Read the React Quick Start.** Read the introductory "Learn React" section at [react.dev/learn](https://react.dev/learn) (about two hours) and then [Thinking in React](https://react.dev/learn/thinking-in-react).
3. **Do the official tic-tac-toe tutorial** at [react.dev/learn/tutorial-tic-tac-toe](https://react.dev/learn/tutorial-tic-tac-toe). Type the code out yourself rather than copying it. The tutorial covers components, props, state, and lifting state up in one sitting.
4. **Read our code in this order.** Each file builds on the previous one: `main.tsx`, then `App.tsx`, then `components/Card.tsx`, then `lib/format.ts`, then `lib/api.ts`, then `components/DataState.tsx`, then `pages/Overview.tsx`, and finally `pages/Consultants.tsx`, which is the richest page (search, filters, pagination, and a detail view).
5. **Change things and observe.** Start the development server (`cd web && npm run dev`, which serves on port 5173 with hot reload). Change a KPI label and watch the page update. Change the delay in `useDebounced` to 3000 milliseconds and notice how sluggish the search feels. Stop the API container and observe what `DataState` renders. When you are done, undo your changes with `git checkout -- .`
6. **Trace one request from end to end.** Open the browser developer tools, go to the Network tab, and load `/consultants`. Find the request to `/api/consultants`, look at the JSON response, then find the matching model in `api/app/models.py` and the matching type in `web/src/lib/types.ts`. After this exercise you understand the entire contract between frontend and backend.
7. **A small first pull request from each of you, separately.** Add one test case to `lib/format.test.ts`, for example an edge case of `parseSkills` or `formatPercent`. It is small on purpose. The goal is to walk through the full workflow once: create a branch, make the change, run the tests, push, open a pull request, get it reviewed by the other person, see the checks pass, and merge.

---

## 6. Task split

The task list lives in [docs/TASKS.md](TASKS.md), with one detailed brief per task in `docs/tasks/`. Each brief lists the target endpoint, which existing file to use as a starting point, and ordered steps. The placeholder pages in the running application (the ones marked "coming soon") show the same briefs in the user interface.

The split is based on your backgrounds. Shravani takes the user interface and product track: tables, filters, and new dashboard pages. Manikanta takes the platform and quality track: tooling, theming, and the pages closest to the infrastructure and AI services, which builds on his cloud and DevOps experience. You will both end up with the same React skills; you are simply approaching them from different directions.

### Shravani: user interface and product track

| Order | Task | Brief | What you will learn |
|---|---|---|---|
| S1 | **WEB-01: Make the consultants table sortable.** This is labeled as a good first issue. | [WEB-01](tasks/WEB-01-sortable-consultants-table.md) | Using `useState` for the sort column and direction, sorting arrays, and click handlers. |
| S2 | **WEB-02: Store the filters in the URL** so that a filtered view can be shared or bookmarked. | [WEB-02](tasks/WEB-02-filters-in-the-url.md) | React Router's [`useSearchParams`](https://reactrouter.com/en/main/hooks/use-search-params) hook, and the idea of treating the URL as state. Every production dashboard needs this. |
| S3 | **WEB-03: Build the Client Health dashboard**, a complete new page. | [WEB-03](tasks/WEB-03-client-health-page.md) | The full recipe for a page: a route, a NAV entry, `useApi`, `ChartCard`, and tests. This task is blocked until API-03 is done, because the endpoint it needs does not exist yet, so coordinate on timing. |

### Manikanta: platform and quality track

| Order | Task | Brief | What you will learn |
|---|---|---|---|
| M1 | **WEB-06 (new task): Add ESLint and Prettier, wired into CI.** Write the task brief yourself in `docs/tasks/`, copying the format of an existing brief. | To be written | The repository currently has no JavaScript linting at all (the Python side has ruff, and the web CI job only checks types). Set up [ESLint with typescript-eslint](https://typescript-eslint.io/getting-started/), add the [eslint-plugin-react-hooks](https://react.dev/reference/rules/rules-of-hooks) plugin (it mechanically enforces React's Rules of Hooks), add [Prettier](https://prettier.io/docs/), create an `npm run lint` script, and add that script to the web CI job. This is a DevOps-shaped task that requires you to touch every configuration file in `web/`. |
| M2 | **WEB-05: Add a light theme and re-validate the chart colors.** | [WEB-05](tasks/WEB-05-light-theme.md) | Design tokens in practice, the `prefers-color-scheme` media query, and why `charts/theme.ts` has to duplicate color values (Recharts cannot read CSS variables). |
| M3 | **AI-04: Build the "Ask your data" page**, a chat-style page that talks to the assistant service. | [AI-04](tasks/AI-04-ask-your-data-page.md) | Making POST requests (this means extending `lib/api.ts`), controlled form inputs, and rendering the generated SQL next to each answer. The task also involves the proxy configuration that routes `/api/assistant` to port 8100 in both nginx and Vite, where your infrastructure knowledge applies directly. This task is blocked until AI-01 is done. |

**WEB-04 (the Timesheet and Billing dashboard)** is unassigned for now because it is blocked on API-04. Whoever finishes their track first takes it, ideally working together with whoever builds the API endpoint.

### Working agreement

- **Pace:** work on one task at a time, in the order listed. Aim to start S1 and M1 in your second week. Do not rush; for the first month, understanding matters more than speed.
- **Review:** Shravani reviews Manikanta's pull requests and Manikanta reviews Shravani's, before the senior review.
- **When you are stuck:** if you have been blocked on the same error for more than 30 minutes, ask in the team channel. Asking early is the expected behavior; staying stuck quietly is the only wrong choice.
- **When a task is blocked by a missing endpoint** (WEB-03, WEB-04, AI-04): either build the page against hard-coded sample data first, or take on the API task itself with help. Each task brief lists its dependencies under `depends_on`.

---

## 7. Glossary: terms you will hear in every React team

- **SPA (single-page application):** one HTML file; JavaScript renders all the pages and switches between them in the browser.
- **Component, props, state, hooks:** see section 2.
- **Server state versus UI state:** data owned by the backend and cached on the client, versus temporary interaction state such as an open menu. Teams use different tools for each.
- **SSR (server-side rendering) and hydration:** the server sends fully rendered HTML, and React then attaches its event handlers to it, which is called hydration. We do not do this; frameworks such as [Next.js](https://nextjs.org/docs) do. You should know the term because it comes up constantly.
- **Code splitting (lazy loading):** shipping only the JavaScript that the current page needs, using [`React.lazy`](https://react.dev/reference/react/lazy).
- **Design tokens:** named CSS variables for colors and spacing, so that a theme is data rather than code.
- **Design system:** an organization-wide shared component library. Our `components/` folder is the beginning of one.
- **Error boundary:** a component that catches a crash during rendering and shows a fallback message instead of a blank page. See [the documentation](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary). This would be a good future task for us.
- **Memoization:** using `useMemo` or `React.memo` to skip repeated computation or re-rendering. Do not reach for it yet. Measure first; adding memoization before measuring is the classic beginner mistake. See the [useMemo documentation](https://react.dev/reference/react/useMemo).
- **Accessibility (often abbreviated a11y):** making the application usable by everyone, including people who use screen readers or only a keyboard. The table toggle in our `ChartCard` is an accessibility feature. A good starting point is [MDN's accessibility guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility).
- **CDN, load balancer, horizontal scaling:** how the static frontend and the API are each scaled in production. See section 3.9.

## 8. Recommended reading (primary sources only)

- **React:** [react.dev/learn](https://react.dev/learn) is the modern documentation. Ignore any tutorial that teaches class components or links to `legacy.reactjs.org`; that material is outdated.
- **React API reference:** [react.dev/reference/react](https://react.dev/reference/react)
- **TypeScript:** [the Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) and the [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- **Vite:** [vite.dev/guide](https://vite.dev/guide/)
- **React Router version 6:** [reactrouter.com](https://reactrouter.com/en/main)
- **Vitest:** [vitest.dev/guide](https://vitest.dev/guide/) and **Testing Library:** [testing-library.com](https://testing-library.com/docs/react-testing-library/intro/)
- **Recharts:** [recharts.org](https://recharts.org/en-US/)
- **MDN** for HTML, CSS, JavaScript, and HTTP fundamentals: [developer.mozilla.org](https://developer.mozilla.org/)
- **This repository:** [web/README.md](../web/README.md), [ARCHITECTURE.md](ARCHITECTURE.md), [TASKS.md](TASKS.md), and [CONTRIBUTING.md](../CONTRIBUTING.md)

Welcome to the team. Aim to open your first pull request this week.
