# Implementation Plan: LeisureLedger

**Objective:** Create a lightweight Flask application with PostgreSQL to track various types of media (movies, games, books, theater, TV seasons).

## Architecture & Data Models
The application uses separate database tables for each media type to capture specific metadata.

### Common Fields
- `id` (Primary Key)
- `title`
- `date_finished` / `date_watched`
- `release_year`
- `is_revisit` (Boolean: Reread/Replay/Rewatch)
- `external_id` (ID from TMDB, Google Books, or IGDB)

### Specific Models
- **Movie**: `provider`, `director`, `writer`, `leading_actors`, `runtime`, `certification`, `budget`, `revenue`, `plot`, `trailer_url`
- **Game**: `publisher`, `developer`, `platform_played`, `original_platform`, `franchise`, `status`, `summary`, `genres`, `user_score`, `critic_score`, `variant`
- **Book**: `author`, `format`, `storygraph_rating`, `summary`, `page_count`, `genres`
- **Theater**: `location`, `original_theater`, `run_time`, `show_type`, `summary`
- **TVSeason**: `series_title`, `season_number`, `network`, `episode_count`, `user_score`, `plot`
- **Goal**: `year`, `movie_goal`, `tv_goal`, `game_goal`, `book_goal`
- **FutureMediaGoal**: `year`, `category`, `title`, `is_completed`

## Tech Stack
- **Backend**: Python 3.12.3, Flask, Flask-SQLAlchemy, Psycopg2
- **Database**: PostgreSQL (Railway)
- **Frontend**: Plain HTML (Jinja2), Vanilla JS, CSS
- **APIs**: TMDB (Movies/TV), Google Books / OpenLibrary (Books), IGDB (Games), IBDB Scraper / Wikipedia / Wikidata (Theater)

## Completed Phases
1. [DONE] **Scaffolding**: Initialize repo and define schema models.
2. [DONE] **Authentication**: Flask-Login with Admin/Read-only split.
3. [DONE] **API Integration**: Build search services for Movies, TV, Games, and Books.
4. [DONE] **CRUD Implementation**: Web forms and table views for all media types.
5. [DONE] **Theater Integration**: Live IBDB search, Wikipedia descriptions, and manual poster uploads.
6. [DONE] **Goals & Statistics**: Yearly targets, historical benchmarks, dual-progress bars, and star-based rewards.
7. [DONE] **Deployment**: Fully deployed on Railway with persistent asset storage.
