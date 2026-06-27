# LeisureLedger Engineering Standards

## Project Identity
- **Name**: LeisureLedger
- **Branding**: Minimalist grayscale palette, 'Inter' font, mobile-friendly design inspired by Ugmonk/Ramp.
- **Mission**: A comprehensive, premium tracking suite for Cinema, Television, Gaming, Literature, and the Arts.

## Architecture
- **Framework**: Flask (Python 3.12.3)
- **Database**: PostgreSQL (SQLAlchemy + Flask-Migrate)
- **Frontend**: Vanilla JS, Jinja2, CSS variables for theming.
- **Persistent Storage**: `/app/app/static/posters` is used for all media artwork (Railway volume mount). **NEVER** use hotlinking for posters.

## Core Metadata Services
- **Movies/TV**: TMDB API (via `TMDBService`).
- **Games**: IGDB API (via `IGDBService`).
- **Books**: Google Books API primary, OpenLibrary fallback on 429 errors (via `GoogleBooksService` / `OpenLibraryService`).
- **Theater**: Live scraping from Internet Broadway Database (IBDB) + Wikipedia/Wikidata for descriptions, runtimes, and posters.

## UX Guidelines
- **Sorting**: All media lists sort by completion/watch date in **ascending order** (oldest first).
- **Visibility**: Title details are **collapsed by default** to maintain a clean "ledger" look.
- **Search Flow**: "Inline Confirmation" - selection of a search result triggers a focused tracking form.
- **Venue**: Default theater venue is "Orpheum".
- **Tracking**: Admin credentials required for all Create/Update/Delete operations.
- **Privacy Mode**: Support for private entries (`is_private` flag) which hide items from list views and dashboard 'Recent' lists for logged-out visitors, while still aggregating into overall totals.
- **Session Persistence**: Persistent login session using `remember=True` cookie duration.
- **Mobile Navigation**: Pure-CSS grid wrapping responsive layout to expose all navigation links on mobile viewports.
- **Metrics**: Admin-only metrics view supporting calendar year and "All Time" filters. Aggregates and displays author, format, platform, provider, and revisit percentages via custom distribution bars.

## Goal System
- **Yearly Tracking**: Goals are scoped to specific calendar years.
- **Dual Progress**: Dashboard displays two bars:
    - **New Media**: Excludes revisits (primary goal driver).
    - **All Media**: Total count including revisits (styled in red).
- **Star Rewards**: Complete specific "Target Titles" set in the Goals page to earn up to 3 ⭐ per category on the dashboard.
- **Validation**: Manual "Validate All Targets" button on the Goals page to retroactively sync ledger data with targets.

## Deployment
- **Platform**: Railway
- **Process**: `Procfile` executes `flask db upgrade` on startup to ensure schema consistency.
- **Integrity**: Always use `Text` fields for potentially long API strings (genres, authors, descriptions) to prevent truncation errors.
