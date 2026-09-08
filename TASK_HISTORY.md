# LeisureLedger TASK_HISTORY.md

## Current Backlog
- None. All tasks completed.

## 2026-09-08 17:04:00
- Merged `dev` branch into `main` and pushed to `origin/main` (Production Rollout):
  - Released Up Next tracking metadata confirmation modal and backend metadata persistence to Production.
  - Automatically triggered Railway Production deployment.
  - Switched back to `dev` for ongoing work.

## 2026-09-08 16:56:00
- Hardened Up Next modal triggers in `app/templates/backlog.html`:
  - Replaced inline JavaScript object parameters in `onclick` with HTML `data-*` attributes (`data-id`, `data-category`, `data-title`, `data-poster`, `data-year`, `data-season`, `data-platform`, `data-format`).
  - Fixed `Uncaught SyntaxError: Unexpected end of input` caused by quote collisions in rendered HTML attributes.
  - Successfully tested and pushed to `origin/dev`.

## 2026-09-08 16:50:00
- Implemented Metadata Confirmation Modal for Up Next tracking:
  - Updated `app/templates/backlog.html` to trigger an inline confirmation modal on "Track" button click instead of an immediate blind POST.
  - Modal prompts for completion date (`date_watched` / `date_finished`), revisit toggle (rewatch / replay / reread), privacy toggle (`is_private`), and category-specific fields (Movie/TV provider location, TV season number, Game platform, franchise & playthrough variant, Book format & StoryGraph rating).
  - Updated `track_up_next_item` in `app/routes.py` to parse and persist all submitted metadata attributes when instantiating new media records.
  - Passed `distinct_franchises` and `now` to `backlog.html` across authenticated and public profile routes.
  - Verified with automated test suite covering all four categories and pushed to `origin/dev`.

## 2026-08-25 15:51:00
- Merged `dev` branch into `main` and pushed to `origin/main` (Production Rollout):
  - Released authenticated Help & User Guide page (`/help`) to Production.
  - Exposes "📖 User Guide & Help" button on home page dashboard hero exclusively for logged-in users.
  - Automatically triggered Railway Production deployment.
  - Switched back to `dev` for ongoing work.

## 2026-08-25 15:47:00
- Refined Help & User Guide content (`app/templates/help.html`):
  - Added user note on Stage Theater artwork explaining limited coverage, Wikipedia follow-up image searches, and custom image upload support.
  - Removed internal design context card ("Private Storage & Isolation").
  - Removed technical column name `(is_private)` from Per-Item Privacy Toggle heading.
  - Removed "Administrator Controls" card and refactored section into "Account & Profile Settings".
  - Verified clean template rendering and pushed to `origin/dev`.

## 2026-08-19 15:49:00
- Completed implementation of the Backlog feature (both Phase 1 and Phase 2).
- Added `BacklogItem` model, context configuration, and database migration.
- Implemented backend routing for adding, deleting, and single-click tracking items.
- Added new templates (`backlog.html`) and modified search and navigation files.
- Successfully verified SQLite database operations using the verification script.

## 2026-08-19 16:01:00
- Completed Goal Search UI & Backlog Integration feature.
- Updated `FutureMediaGoal` model and migrated the database to add `external_id`.
- Reworked goals target addition flow to use unified API search templates.
- Added `POST /goals/add/<category>/<external_id>` route.
- Implemented goals/backlog cross-correlation (star markers on backlog, queued badges on goals page).
- Updated validation and delete triggers to match goals by `external_id` (with title string fallback).
- Successfully verified integration with the verification script.

## 2026-08-19 16:11:00
- Completed Goals UI Unification and Queue Action feature.
- Expanded `FutureMediaGoal` model to include `poster_path` and `release_year`.
- Migrated database schema to apply the new columns.
- Updated `get_tv_details` in `app/services.py` to return TV show first air date.
- Reworked `add_goal_target` to query, download, and store poster path and release year.
- Implemented `POST /goals/queue/<goal_id>` to add target items directly to the backlog.
- Redesigned `goals.html` target listings into card grids matching `backlog.html`.
- Added Queue button form (with limit validation of 10) on target cards.
- Successfully verified integration with the verification script.

## 2026-08-19 16:18:00
- Completed Up Next Rebranding.
- Renamed all `/backlog` URL routes and views in `app/routes.py` to `/up-next` and `up_next`.
- Updated navigation link in `app/templates/base.html` to target the new page.
- Rebranded heading and sub-items in `app/templates/backlog.html` and added a short-term description at the top of the page.
- Updated badges, tooltips, and disabled states in `app/templates/goals.html` to reference Up Next.
- Renamed backlog parameter logic and buttons to Up Next in search templates.
- Successfully verified Flask route registration using the verification script.

## 2026-08-19 16:37:00
- Completed Search & Actions Unification feature.
- Swapped external search inputs and local filters on media list templates (`movies.html`, `tv.html`, `games.html`, `books.html`, `theater.html`).
- Integrated column-top search inputs inside Up Next and Goals list pages.
- Modified `search_movie`, `search_tv`, `search_game`, and `search_book` in `app/routes.py` to forward context parameters.
- Overhauled search templates (`movie_search.html`, `tv_search.html`, `game_search.html`, `book_search.html`) to use a single "Select" card button and a unified tabbed details confirmation block (Track, Up Next, Goals).
- Confirmed template rendering and routing setup using automated verification scripts.

## 2026-08-19 16:43:00
- Protected external search boxes: wrapped them with `{% if current_user.is_authenticated %}` on `movies.html`, `tv.html`, `games.html`, `books.html`, and `theater.html` templates to hide them for logged-out users.
- Added category-selectable universal search form to `index.html` (homepage hero section) for authenticated users.
- Commited and pushed changes to origin main branch.

## 2026-08-19 16:50:00
- Redesigned search templates confirmation panels: replaced the clumsy tabbed interface with a responsive 3-column side-by-side action card grid.
- Implemented auto-highlighting border and "Recommended" badge on active action card based on search page navigation parameters.
- Updated `walkthrough.md` with new layout specifications and verified operations.

## 2026-08-20 07:06:00
- Fixed DOM nesting bug in `book_search.html` (removed duplicate opening div) that caused the confirmation card container to become hidden on selection.
- Hardened `movie_search.html`, `tv_search.html`, `game_search.html`, and `book_search.html` to pass selection details via `data-*` attributes for safe parsing of titles with quotes and special characters.
- Added top-level universal category search forms to `backlog.html` (Up Next) and `goals.html` for authenticated users.

## 2026-08-20 07:09:00
- Set default format to "Audiobook" in both the Track Completed and Queue Up Next action cards on `book_search.html`.

## 2026-08-24 12:40:00
- Fixed `backup.bat` to invoke `.venv\Scripts\python.exe` directly, preventing `ModuleNotFoundError: No module named 'dotenv'` when system Python is in PATH.
- Added argument forwarding `%*` to `backup.bat` to support `--restore` and custom flags.
- Updated `backup_db.py` to include `BacklogItem` model in both `backup()` and `restore()` dictionary mappings.

## 2026-08-24 13:00:00
- Added interactive main menu to `backup_db.py` (`1. Backup`, `2. Restore`, `3. Exit`).
- Implemented automatic backup file discovery and numbered selection from `./backups/` for streamlined restore into dev databases.

## 2026-08-24 13:09:00
- Implemented `manage_volume.py` and `volume.bat` utility for out-of-band persistent storage management.
- Supports ZIP poster backup export/import, source API air-gapped re-fetching, and direct out-of-band downloading of media assets from production URL.
- Updated `.gitignore` to track volume maintenance tools and backup archives.

## 2026-08-24 13:22:00
- Tracked `manage_volume.py`, `volume.bat`, `backup_db.py`, and `backup.bat` in Git repository so they are included in Railway deployment builds for remote container executions.

## 2026-08-24 13:28:00
- Completed Module 1 of Multi-User Support: Schema updates & Alembic migration (`e1a2b3c4d5e6`).
- Added `is_admin` to `User` model with automatic migration upgrade promoting existing user(s) to Admin.
- Added `InviteToken` model supporting single-use token onboarding for closed registration.
- Added `user_id` foreign keys, indices, and constraints across `Movie`, `Game`, `Book`, `Theater`, `TVSeason`, `Goal`, `FutureMediaGoal`, and `BacklogItem`.
- Safely backfilled `user_id = 1` for all existing records.
- Verified migration upgrade and data integrity on local database.

## 2026-08-24 13:35:00
- Updated all 14 model instantiation points across `app/routes.py` (`Movie`, `TVSeason`, `Game`, `Book`, `Theater`, `Goal`, `FutureMediaGoal`, `BacklogItem`) to pass `user_id=current_user.id`.
- Verified insertion and deletion operations.

## 2026-08-24 13:43:00
- Completed Phase 2 of Multi-User Support: Direct Admin User Management & Account Settings.
- Implemented `@admin_required` access control decorator in `app/routes.py`.
- Built Admin User Management dashboard (`/admin/users`) with user creation, password reset, role promotion/demotion, and account deletion with data cleanup.
- Built User Account Settings page (`/account`) allowing users to change their own passwords.
- Added navigation links for Admin and Account in `base.html`.
- Verified authentication, permission boundaries, and template rendering with automated test suite.

## 2026-08-24 13:50:00
- Implemented automatic PostgreSQL primary key sequence synchronization in `app/__init__.py` on application startup and in `backup_db.py` on restore completion to prevent duplicate key collisions (`user_pkey`) after database dumps/restores.

## 2026-08-24 13:56:00
- Completed Phase 3 of Multi-User Support: Full Query Isolation & Scoped CRUD Operations.
- Scoped ledger queries across all media categories (`Movie`, `TVSeason`, `Game`, `Book`, `Theater`) to `active_user_id` / `current_user.id`.
- Scoped homepage dashboard (`index`), `up_next` queue, `metrics`, and `goals` stats to the authenticated user.
- Enforced strict IDOR protection on all record edit, replacement, and deletion endpoints (`/movies/edit/<id>`, `/tv/delete/<id>`, `/up-next/delete/<id>`, etc.).
- Scoped target map lookup in `inject_globals` context processor to active user.
- Passed 100% of end-to-end multi-user isolation, IDOR, and privilege boundary automated tests.

## 2026-08-24 13:58:00
- Added Non-Production environment indicators:
  - Browser tab title prefix (e.g. `[DEV] LeisureLedger`).
  - Top viewport warning banner (`⚠️ DEV ENVIRONMENT — Non-Production Instance`).
  - Navbar logo brand badge (`DEV` / `STAGING`).
  - Automatic detection in `config.py` using Railway environment variables.

## 2026-08-24 14:01:00
- Fixed dashboard total count display in `app/templates/index.html` for Books and Theater: replaced direct un-scoped ORM calls (`Book.query.count()`, `Theater.query.count()`) with scoped `book_count` and `theater_count` variables passed from `app/routes.py`.

## 2026-08-24 14:10:00
- Enforced strict authentication boundary:
  - Root `/` and all media listing pages (`/movies`, `/tv`, `/games`, `/books`, `/theater`, `/up-next`) now strictly redirect unauthenticated visitors directly to `/login`.
- Implemented Public Ledger Profiles & Vanity URL system:
  - Added `is_public` boolean column to `User` model with Alembic migration `f2b3c4d5e6a7`.
  - Added Public Ledger sharing toggle and shareable link with clipboard copy in `/account` settings.
  - Implemented public vanity routes (`/<username>`, `/<username>/movies`, `/<username>/tv`, `/<username>/games`, `/<username>/books`, `/<username>/theater`).
  - Created `public_user_index.html` dashboard and updated media templates to cleanly render public items while hiding private entries (`is_private=True`), search forms, and edit/delete controls.
  - Added collision protection with reserved application routes.

## 2026-08-24 14:15:00
- Updated dashboard hero header in `app/templates/index.html` to display personalized greeting: `Welcome back, <username>.`

## 2026-08-24 14:18:00
- Added category subtitle taglines below page headings matching the hero style:
  - Movies, TV, Theater: `Whatcha watchin?`
  - Games: `Whatcha playin?`
  - Books: `Whatcha readin?`

## 2026-08-24 14:24:00
- Added "Up Next" queue to public user profile system:
  - Added `is_up_next_public` boolean column to `User` model with Alembic migration `b4d5e6f7a8b9`.
  - Added sub-option toggle checkbox in `/account` settings (`Include "Up Next" queue on my public profile`).
  - Added public vanity route `/<username>/up-next` and updated `backlog.html` to support read-only visitor mode (hiding queue search forms, track buttons, and remove buttons).
  - Added dynamic Up Next card to `public_user_index.html` and public navbar link in `base.html` when `is_up_next_public` is enabled.

## 2026-08-24 14:29:00
- Merged `dev` branch to `main` and pushed to `origin/main` (Phase 5 Production Rollout):
  - Automatically triggered Railway Production deployment.
  - Procfile automatically executes `flask db upgrade` on startup applying migrations `e1a2b3c4d5e6`, `f2b3c4d5e6a7`, and `b4d5e6f7a8b9`.
  - Backfills all historical media to primary admin user (`user_id=1`).
  - Switched back to `dev` for ongoing work.
