# Implementation Plan: Media Tracker Application

**Objective:** Create a lightweight Flask application with PostgreSQL to track various types of media (movies, games, books, theater, TV seasons).

## Architecture & Data Models
The application will use separate database tables for each media type to capture specific metadata identified from the legacy Google Sheets.

### Common Fields
- `id` (Primary Key)
- `title`
- `date_finished` / `date_watched`
- `release_year`
- `is_revisit` (Boolean: Reread/Replay/Rewatch)
- `external_id` (ID from TMDB, Google Books, or RAWG)

### Specific Models
- **Movie**: `provider`, `director`, `leading_actors`
- **Game**: `publisher`, `platform_played`, `original_platform`, `franchise`, `status` (Backlog, In Progress, Finished, DNF)
- **Book**: `author`, `format`, `goodreads_rating`
- **Theater**: `location`
- **TVSeason**: `series_title`, `season_number`, `network`, `episode_count`
- **Goal**: `year`, `title`, `format`, `completed`

## Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, Psycopg2
- **Database**: PostgreSQL
- **Frontend**: Plain HTML, Vanilla CSS
- **APIs**: TMDB (Movies/TV), Google Books (Books), RAWG/IGDB (Games)

## Development Phases
1. **Scaffolding**: Initialize repo and define schema models.
2. **API Integration**: Build search services for external media databases.
3. **CRUD Implementation**: Create web forms and table views for each media type.
4. **Dashboard**: Unified view for recently consumed media and goals tracking.
