# LeisureLedger

A lightweight, premium web application for tracking your journey through cinema, television, gaming, literature, and the arts.

## Features
- **Multi-Media Tracking**: Dedicated systems for Movies, TV Seasons, Games, Books, and Theater Productions.
- **Rich Metadata Integration**:
    - **Movies/TV**: Powered by TMDB.
    - **Games**: Powered by IGDB.
    - **Books**: Powered by Google Books and OpenLibrary.
    - **Theater**: Live scraping from IBDB with Wikipedia/Wikidata enrichment for summaries and runtimes.
- **Visual Ledger**: Beautiful, minimalist design with local poster storage (no hotlinking).
- **Yearly Goals**: 
    - Set specific targets for each category.
    - Dual-progress bars (New Media vs. All Media).
    - Earn ⭐ icons for completing specific "Target Titles" each year.
- **Historical Insights**: Browse your tracking history and goal progress by year.
- **Admin Security**: Flask-Login protected Create/Update/Delete operations.

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: PostgreSQL (SQLAlchemy)
- **Asset Storage**: Persistent local volume for posters.
- **Deployment**: Optimized for Railway.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set environment variables for API keys (TMDB, IGDB, Google Books).
4. Run migrations: `flask db upgrade`.
5. Start the app: `python run.py`.
