# LeisureLedger Engineering Standards & Antigravity Agent Rules

## 1. Antigravity Interaction & Gating Protocol
* **Role:** Senior Full-Stack Architect & Systems Engineer.
* **Explicit Gating & Intent Confirmation:**
  * Before executing modifications, database migrations, package installations, or script runs, you must provide a clear summary of your intended changes and explicitly ask:
    > *"Here's what I'm going to do: [Summary of steps/changes]. Shall I proceed?"*
  * Wait for affirmative user confirmation before modifying files or issuing terminal commands.
* **Separation of Planning vs. Execution:**
  * If a prompt is conceptual, exploratory, or asks "how to approach" a problem, provide design options, trade-offs, and modular steps ONLY. Do not execute commands or edit code.
* **Modular Execution & Checkpoints:**
  * Implement changes one discrete, testable sub-module at a time.
  * Pause after each module to report status and confirm the next step.
  * **No Unbounded Loops:** If an action, build, or test fails twice consecutively, halt execution immediately, document the root cause in the chat, and request guidance.
* **Local Audit Trail:**
  * Maintain a `./TASK_HISTORY.md` file in the repo tracking timestamps, modified files, executed commands, and current backlog.

---

## 2. Observability & Runtime Logging (Railway Standards)
* **Standard Output Logging:** Configure all Python/Flask application logging to write structured logs directly to `stdout` (`sys.stdout`) so they stream into Railway's Deployment Logs and Log Explorer.
* **Severity Formatting:** Explicitly map log handlers to avoid default Python `stderr` routing (which marks all logs as errors in Railway). Ensure clean `INFO`, `WARNING`, and `ERROR` outputs with relevant contextual metadata (endpoint, user ID, API response codes).
* **Exception Handling:** All service integrations and critical routes must catch exceptions cleanly, log the traceback to `sys.stdout` / Railway runtime logs, and return user-safe errors.

---

## 3. Project Identity & Core Architecture
* **Name**: LeisureLedger
* **Branding**: Minimalist grayscale palette, 'Inter' font, mobile-friendly design inspired by Ugmonk/Ramp.
* **Mission**: A comprehensive tracking suite for Cinema, Television, Gaming, Literature, and the Arts.
* **Framework**: Flask (Python 3.12.3)
* **Database**: PostgreSQL (SQLAlchemy + Flask-Migrate). Always use `Text` fields for variable-length API strings (genres, authors, descriptions) to prevent truncation.
* **Frontend**: Vanilla JS, Jinja2, CSS variables for theming.
* **Persistent Storage**: `/app/app/static/posters` (Railway volume mount). **NEVER** use hotlinking for media artwork.
* **Deployment**: Railway platform. `Procfile` executes `flask db upgrade` on startup.

---

## 4. Metadata Integration Services
* **Movies/TV**: TMDB API via `TMDBService`.
* **Games**: IGDB API via `IGDBService`.
* **Books**: Google Books API primary, OpenLibrary fallback on 429 errors via `GoogleBooksService` / `OpenLibraryService`.
* **Theater**: Live scraping via Internet Broadway Database (IBDB) + Wikipedia/Wikidata for descriptions, runtimes, and poster art.

---

## 5. UX & Application Behaviors
* **Sorting**: All media lists sort by completion/watch date in **ascending order** (oldest first).
* **Visibility**: Title details are **collapsed by default** to preserve the clean ledger look.
* **Search Flow**: "Inline Confirmation" — selecting a search result opens a focused tracking form.
* **Defaults**: Default theater venue is `"Orpheum"`.
* **Access Control**: Admin credentials required for all Create, Update, and Delete operations.
* **Privacy Mode**: `is_private` flag hides entries from public list views and dashboard "Recent" lists for unauthenticated users, while retaining aggregation in overall totals.
* **Session Persistence**: Persistent login session using `remember=True` cookie settings.
* **Mobile Layout**: Pure-CSS grid wrapping responsive layout exposing all navigation items on mobile viewports.
* **Metrics View**: Admin-only view supporting calendar year and "All Time" views with custom distribution bars (author, format, platform, provider, revisit rates).

---

## 6. Goal System
* **Scope**: Goals are strictly bound to individual calendar years.
* **Progress Tracking**: Dual-bar dashboard display:
  * **New Media**: Excludes revisits (primary goal driver).
  * **All Media**: Total count including revisits (styled in red).
* **Star Rewards**: Completing assigned "Target Titles" awards up to 3 ⭐ per category on the dashboard.
* **Sync & Validation**: Manual "Validate All Targets" button on the Goals page to retroactively reconcile ledger entries against targets.