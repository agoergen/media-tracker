# LeisureLedger TASK_HISTORY.md

## Current Backlog
- None. All tasks completed.

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
