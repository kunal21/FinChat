# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinChat is an AI-powered portfolio impact notification platform that monitors financial news and alerts users to events affecting their investments. Built with Flask (Python), React (TypeScript), PostgreSQL, and integrated with Plaid (banking), Finnhub (news), and OpenAI (LLM analysis).

## Development Commands

### Starting the Application

```bash
# Start all services (recommended)
docker compose up --build

# Start in detached mode
docker compose up --build -d

# Start with debug configuration (hot-reload enabled)
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build

# View logs
docker compose logs --follow
docker compose logs --follow server  # specific service
```

The application runs at:
- Client: http://localhost:3001
- Server API: http://localhost:5001
- Ngrok Dashboard: http://localhost:4040
- Database: localhost:5432

### Running Batch Jobs

```bash
# News ingestion (portfolio impact analysis)
docker compose exec server python portfolio_impact/jobs/batch_job.py

# Plaid transaction sync
docker compose exec server python jobs/update_transactions.py

# Seed test holdings data
docker compose exec server python scripts/seed_fake_holdings.py
```

### Database Operations

```bash
# Access PostgreSQL shell
docker compose exec db psql -U postgres

# Run migrations
docker compose exec server alembic upgrade head

# Create new migration
docker compose exec server alembic revision --autogenerate -m "Description"

# Rollback migration
docker compose exec server alembic downgrade -1
```

### Frontend Development

```bash
# Inside client container
npm start        # Start dev server (PORT=3001)
npm run build    # Production build
npm test         # Run tests
npm run lint     # ESLint
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: clears database)
docker compose down -v

# Restart specific service
docker compose restart server
```

## Architecture

### Multi-Service Docker Setup

Four containerized services orchestrated via docker-compose:
- **db**: PostgreSQL 11.2 with persistent volume (`pg_${PLAID_ENV}_data`)
- **server**: Flask Python backend (port 5001)
- **ngrok**: Webhook tunnel for Plaid callbacks (port 4040 dashboard)
- **client**: React TypeScript frontend (port 3001)

Volume mounts enable hot-reload during development:
- `./server_python:/app` - Python code changes auto-reload
- `./client:/opt/client` - React hot module replacement

### Backend Architecture (server_python/)

**Flask Application Lifecycle** ([app.py](server_python/app.py)):
1. Load environment variables via dotenv
2. Initialize Flask app with CORS for frontend origin
3. Initialize database with SQLAlchemy (`init_db()`)
4. Import all models to register with SQLAlchemy
5. Initialize Socket.IO for real-time messaging
6. Register all blueprints from `routes/__init__.py`
7. Store socketio instance in `app.config['socketio']`
8. Run with socketio.run() (not app.run())

**Directory Structure**:

```
server_python/
├── app.py                      # Flask app factory and Socket.IO setup
├── db/                         # Database configuration
│   ├── __init__.py            # SQLAlchemy initialization, init_db()
│   ├── config.py              # DB connection settings from env vars
│   └── queries.py             # Common query helpers
│
├── models/                     # SQLAlchemy ORM models
│   ├── __init__.py            # Exports all models, TimestampMixin
│   ├── user.py                # User model with relationships
│   ├── holding.py             # Investment holdings (Plaid)
│   ├── article.py             # News articles (ticker, processed, is_material)
│   ├── user_impact.py         # Portfolio impact notifications
│   └── deadletter.py          # Failed operation tracking
│
├── routes/                     # Flask blueprints (API endpoints)
│   ├── __init__.py            # Registers all blueprints in list
│   ├── users.py               # GET/PATCH /users/:id/impacts
│   ├── accounts.py            # Account CRUD
│   ├── messages.py            # Chat messages with Socket.IO
│   └── ...
│
├── integrations/              # External API clients (singleton pattern)
│   ├── plaid_client.py        # PlaidClient singleton
│   ├── openai_client.py       # OpenAIClient singleton
│   └── data/                  # Static integration data
│
├── core/                      # Shared utilities
│   └── utils.py               # sanitize_* functions for API responses
│
├── services/                  # Business logic layer
│   └── summary_generator.py  # Transaction summarization
│
├── portfolio_impact/          # Portfolio impact intelligence system
│   ├── clients/               # News source integrations
│   │   └── finnhub_client.py # Finnhub API wrapper
│   ├── analyzers/             # AI analysis engines
│   │   └── impact_analyzer.py # GPT-4 materiality analysis
│   └── jobs/                  # Batch processing scripts
│       └── batch_job.py       # Main news ingestion orchestrator
│
├── news_ingestion/            # News processing utilities
│   ├── util.py                # URL canonicalization, text cleaning
│   └── pipeline.py            # Deduplication, deadletter insertion
│
├── jobs/                      # General batch jobs
│   └── update_transactions.py # Plaid transaction sync
│
└── migrations/                # Alembic database migrations
    └── alembic.ini
```

### Frontend Architecture (client/)

React 16.14 with TypeScript, proxied to backend via `"proxy": "http://server:5001"` in package.json.

**Key Components**:
- `PortfolioImpact.tsx`: Displays user-specific impact notifications with real-time API data
- `ChatWindow.tsx`: Conversational AI interface with Socket.IO
- `UserPage.tsx`: Main user dashboard with tabbed interface

**API Client** ([services/api.tsx](client/src/services/api.tsx)):
- Axios instance with baseURL to server
- Exports functions: `getUserImpacts()`, `updateUserImpact()`, etc.
- Used by components via `useEffect()` hooks

### Database Schema

**Core Financial Models**:
- `users_table`: User accounts
- `items`: Plaid connection items (1 per linked institution)
- `accounts`: Bank/investment accounts from Plaid
- `holdings`: Investment positions (ticker_symbol, quantity, institution_price)
- `transactions`: Transaction history

**Portfolio Impact Models**:
- `articles`: News articles with columns:
  - `ticker` (VARCHAR(10)): Associated stock ticker
  - `processed` (BOOLEAN): Whether analyzed by LLM
  - `is_material` (BOOLEAN): LLM materiality assessment
  - `structured_data` (JSONB): Full LLM response
  - `canonical_url` (TEXT): Normalized URL for deduplication
- `user_impacts`: User notifications with:
  - `impact_level`: HIGH/MEDIUM/LOW
  - `impact_summary`: AI-generated explanation
  - `estimated_effect`: positive/negative/neutral
  - `read`, `dismissed`: User interaction flags

**System Tables**:
- `deadletter`: Failed operations (stage, url, error, payload_json)
- `plaid_api_events`: Plaid API call logging

### Critical Patterns

#### 1. Singleton Pattern for API Clients

External API clients use singleton pattern to reuse connections:

```python
# integrations/plaid_client.py
class PlaidClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlaidClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # Initialize once
        self.client = plaid_api.PlaidApi(api_client)
        self._initialized = True

# Usage in any module
from integrations.plaid_client import plaid_client
```

**Always import from `integrations/` or `core/`, never from root**:
- ✅ `from integrations.plaid_client import plaid_client`
- ✅ `from core.utils import sanitize_user`
- ❌ `from plaid_client import plaid_client` (deprecated)

#### 2. Flask App Context for Batch Jobs

Batch jobs must create Flask app context to access database:

```python
from app import create_app
from db import db

def main():
    app = create_app()
    with app.app_context():
        # Now db.session works
        users = User.query.all()
        db.session.commit()
```

#### 3. Python Path Handling for Scripts

Scripts in subdirectories need path manipulation to import server modules:

```python
# For scripts in server_python/portfolio_impact/jobs/
from pathlib import Path
import sys

server_python_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(server_python_dir))

# Now can import from server_python root
from app import create_app
from models.user import User
```

#### 4. URL Canonicalization for Deduplication

Before checking if article exists, always canonicalize URL:

```python
from news_ingestion.util import canonicalize_url
from news_ingestion.pipeline import article_exists_by_canonical_url

canonical = canonicalize_url(raw_url)  # Removes UTM params, trailing slashes
if article_exists_by_canonical_url(db.session, canonical):
    # Skip duplicate
```

#### 5. Deadletter Queue for Error Tracking

Failed operations should be logged, not silently dropped:

```python
from news_ingestion.pipeline import insert_deadletter
from models.deadletter import Deadletter

try:
    # Attempt operation
    process_article(article)
except Exception as e:
    deadletter_row = Deadletter(
        stage="impact_analysis",
        url=article["url"],
        error=str(e),
        payload_json=article
    )
    insert_deadletter(db.session, deadletter_row)
    db.session.rollback()
    # Continue processing other items
```

#### 6. LLM Analysis with Retry Logic

Impact analysis uses retry pattern with validation:

```python
from portfolio_impact.analyzers.impact_analyzer import analyze_impact_with_retry

try:
    impact = analyze_impact_with_retry(
        clean_text=article_text,
        ticker=ticker,
        api_key=openai_api_key,
        model="gpt-4o-mini",
        max_attempts=2
    )
    # impact has: is_material, impact_level, impact_summary, etc.
except ValueError as e:
    # Both attempts failed validation
    logger.error(f"Failed to analyze: {e}")
```

#### 7. Sanitization for API Responses

Use `sanitize_*` functions to convert ORM models to JSON-safe dicts:

```python
from core.utils import sanitize_user_impact

@bp.route("/users/<int:user_id>/impacts")
def get_user_impacts(user_id):
    impacts = UserImpact.query.filter_by(user_id=user_id).all()
    return jsonify([sanitize_user_impact(impact) for impact in impacts])
```

These functions handle:
- Converting Decimal to float
- Converting datetime to ISO string
- Embedding related objects (e.g., impact.article)
- Removing None/null fields

## Portfolio Impact Pipeline

The core feature that monitors news and generates personalized alerts.

### Data Flow

1. **Ticker Discovery** (`get_all_user_tickers`):
   - Joins: Holding → Account → Item
   - Returns unique uppercase tickers from user holdings

2. **News Fetching** (`finnhub_client.finnhub_fetch`):
   - Endpoint: `https://finnhub.io/api/v1/company-news`
   - Parameters: ticker, from_date (YYYY-MM-DD), to_date
   - Returns: List of article dicts with title, summary, url, datetime

3. **Deduplication**:
   - Canonicalize URL (remove UTM params, normalize path)
   - Check `article_exists_by_canonical_url()`
   - Skip if article already in database

4. **Article Storage** (`insert_article_with_ticker`):
   - Generate article_id: SHA256(canonical_url + title + published_at)
   - Create Article record with ticker field populated
   - Set processed=False initially

5. **AI Materiality Analysis** (`analyze_impact_with_retry`):
   - Build clean text from title + description + content
   - Prompt GPT-4: "Is this article material for {ticker}?"
   - Returns structured JSON with is_material, impact_level, impact_summary
   - Validates response schema, retries on failure (max 2 attempts)
   - Update Article: set processed=True, is_material, structured_data

6. **User Impact Generation**:
   - If is_material=True:
     - Find all users holding the ticker (`get_users_holding_ticker`)
     - Create UserImpact for each user
     - Generate impact_id: SHA256(user_id + article_id + ticker)
     - Set read=False, dismissed=False
   - If is_material=False: Skip impact creation

7. **Frontend Display**:
   - GET `/users/{userId}/impacts?unread_only=false`
   - Returns impacts with embedded article details
   - User can dismiss (PATCH with `{dismissed: true}`)
   - User can mark read (PATCH with `{read: true}`)

### Running the Pipeline

```bash
# One-time manual run
docker compose exec server python portfolio_impact/jobs/batch_job.py

# Schedule via cron (every 4 hours)
0 */4 * * * docker compose exec server python portfolio_impact/jobs/batch_job.py
```

## Environment Variables

Required in `.env`:

```bash
# Plaid (Banking Integration)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET_SANDBOX=your_plaid_sandbox_secret
PLAID_ENV=sandbox  # or production

# OpenAI (LLM & Embeddings)
OPENAI_CLIENT_ID=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# Finnhub (News)
FINNHUB_API_KEY=your_finnhub_api_key

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=postgres  # NOT "pattern" - use existing DB
DB_HOST_NAME=db  # Docker service name
DB_PORT=5432

# Frontend
FRONTEND_ORIGIN=http://localhost:3001
PORT=5001  # Server port
```

## Adding New Features

### Adding a News Source

1. Create client in `portfolio_impact/clients/new_source_client.py`:
   ```python
   def new_source_fetch(api_key, ticker, from_date, to_date):
       # Fetch from API
       return articles

   def parse_new_source_article(article, ticker):
       # Return dict with: url, title, description, content, published_at, ticker
   ```

2. Update `batch_job.py` to use new source:
   ```python
   from portfolio_impact.clients.new_source_client import new_source_fetch

   # In process_ticker():
   articles = new_source_fetch(api_key, ticker, from_date, to_date)
   ```

### Adding a Route

1. Create `routes/new_feature.py`:
   ```python
   from flask import Blueprint, jsonify

   bp = Blueprint("new_feature", __name__)

   @bp.route("/new-endpoint")
   def handler():
       return jsonify({"message": "Hello"})
   ```

2. Register in `routes/__init__.py`:
   ```python
   from .new_feature import bp as new_feature_bp

   blueprints.append(new_feature_bp)
   ```

### Adding a Batch Job

1. Create `jobs/new_job.py`:
   ```python
   from pathlib import Path
   import sys

   # Add server_python to path
   server_python_dir = Path(__file__).resolve().parent.parent
   sys.path.insert(0, str(server_python_dir))

   from app import create_app
   from db import db

   def main():
       app = create_app()
       with app.app_context():
           # Database operations here
           db.session.commit()
       return 0

   if __name__ == "__main__":
       sys.exit(main())
   ```

2. Run via Docker:
   ```bash
   docker compose exec server python jobs/new_job.py
   ```

### Adding a Database Model

1. Create `models/new_model.py`:
   ```python
   from db import db
   from models import TimestampMixin

   class NewModel(db.Model, TimestampMixin):
       __tablename__ = "new_table"

       id = db.Column(db.Integer, primary_key=True)
       # Add columns
   ```

2. Import in `models/__init__.py`:
   ```python
   from .new_model import NewModel
   ```

3. Create migration:
   ```bash
   docker compose exec server alembic revision --autogenerate -m "Add NewModel"
   docker compose exec server alembic upgrade head
   ```

## Common Issues

### Import Errors in Batch Jobs

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Add Python path handling at top of script:
```python
from pathlib import Path
import sys

server_python_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(server_python_dir))
```

### Database Column Doesn't Exist

**Problem**: `psycopg2.errors.UndefinedColumn: column "ticker" of relation "articles" does not exist`

**Solution**: Model updated but database not migrated. Run:
```bash
docker compose exec db psql -U postgres -c "ALTER TABLE articles ADD COLUMN ticker VARCHAR(10);"
# Or create proper Alembic migration
```

### Socket.IO Not Working

**Problem**: Chat messages not sending

**Solution**: Ensure using `socketio.run()` not `app.run()` in app.py:
```python
socketio = app.config['socketio']
socketio.run(app, host="0.0.0.0", port=port)
```

## Testing Data

### Seed Holdings

```bash
docker compose exec server python scripts/seed_fake_holdings.py
```

Creates investment account with popular stocks (AAPL, MSFT, NVDA, etc.) for all users.

### Run News Ingestion

```bash
docker compose exec server python portfolio_impact/jobs/batch_job.py
```

Fetches last 24 hours of news for seeded tickers and generates impacts.

### Verify in Database

```bash
docker compose exec db psql -U postgres

-- Check articles
SELECT ticker, COUNT(*) FROM articles WHERE ticker IS NOT NULL GROUP BY ticker;

-- Check impacts
SELECT ticker, impact_level, COUNT(*) FROM user_impacts GROUP BY ticker, impact_level;

-- Check errors
SELECT stage, COUNT(*) FROM deadletter GROUP BY stage;
```
