# FinChat Server

Python/Flask backend for the FinChat personal finance application.

## Project Structure

```
server_python/
├── app.py                      # Flask application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
│
├── core/                       # Core utilities and helpers
│   ├── __init__.py
│   └── utils.py               # Data serializers and helper functions
│
├── integrations/              # External API clients
│   ├── __init__.py
│   ├── plaid_client.py        # Plaid banking API client (singleton)
│   ├── openai_client.py       # OpenAI embeddings client (singleton)
│   └── data/                  # Integration data files
│       └── transactions-personal-finance-category-taxonomy.csv
│
├── db/                        # Database configuration and queries
│   ├── __init__.py
│   ├── config.py              # Database connection settings
│   └── queries.py             # Common database queries
│
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   ├── account.py
│   ├── transaction.py
│   ├── holding.py
│   ├── article.py
│   ├── user_impact.py
│   ├── deadletter.py
│   └── ...
│
├── routes/                    # Flask API routes
│   ├── __init__.py
│   ├── auth.py                # Authentication endpoints
│   ├── users.py               # User management
│   ├── accounts.py            # Account operations
│   ├── items.py               # Plaid item management
│   ├── messages.py            # Chat/messaging
│   └── ...
│
├── services/                  # Business logic and services
│   ├── __init__.py
│   └── summary_generator.py  # Transaction summarization
│
├── jobs/                      # Batch jobs and background tasks
│   ├── __init__.py
│   └── update_transactions.py # Plaid transaction sync job
│
├── webhook_handlers/          # Webhook event handlers
│   ├── __init__.py
│   └── transactions.py        # Plaid transaction webhooks
│
├── portfolio_impact/          # Portfolio impact analysis system
│   ├── __init__.py
│   ├── README.md
│   ├── clients/               # News/data source clients
│   │   └── finnhub_client.py
│   ├── analyzers/             # Impact analysis engines
│   │   └── impact_analyzer.py
│   └── jobs/                  # Impact processing jobs
│       └── batch_job.py
│
├── news_ingestion/            # News processing utilities
│   ├── __init__.py
│   ├── util.py                # URL canonicalization, text processing
│   └── pipeline.py            # Article deduplication, deadletter
│
├── prompts/                   # LLM prompts and templates
│   ├── __init__.py
│   └── expenses_prompt.txt
│
├── scripts/                   # Utility scripts
│
└── migrations/                # Database migrations (Alembic)
```

## Key Components

### Core (`core/`)
Common utilities used across the application:
- **utils.py**: Serializers for converting database models to JSON-safe dicts
  - `sanitize_user()`, `sanitize_account()`, `sanitize_transaction()`, etc.

### Integrations (`integrations/`)
External API clients using singleton pattern:
- **PlaidClient**: Banking data from Plaid API
- **OpenAIClient**: Embeddings and LLM capabilities

Import with: `from integrations.plaid_client import plaid_client`

### Models (`models/`)
SQLAlchemy ORM models for database tables:
- Financial: User, Account, Transaction, Holding
- News: Article, Event, UserImpact
- System: Deadletter, PlaidApiEvent

### Routes (`routes/`)
Flask blueprints for API endpoints:
- RESTful endpoints for CRUD operations
- Webhook handlers
- Authentication and authorization

### Services (`services/`)
Business logic separated from routes:
- Transaction summarization
- Vector search integration
- Complex data transformations

### Portfolio Impact (`portfolio_impact/`)
Autonomous system for news analysis and portfolio impact assessment.
See [portfolio_impact/README.md](portfolio_impact/README.md) for details.

### Jobs (`jobs/`)
Batch processing and background tasks:
- **update_transactions.py**: Sync transactions from Plaid
- Designed to run via cron or on-demand

### News Ingestion (`news_ingestion/`)
Utility functions for news processing:
- URL canonicalization
- Text cleaning
- Article deduplication
- Error tracking (deadletter queue)

## Running the Application

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.template .env
# Edit .env with your API keys

# Run Flask app
python app.py
```

### Docker
```bash
docker-compose up
```

## Environment Variables

Required in `.env`:

```bash
# Plaid (Banking)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET_SANDBOX=your_plaid_secret
PLAID_ENV=sandbox

# OpenAI (Embeddings/LLM)
OPENAI_CLIENT_ID=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# Finnhub (News)
FINNHUB_API_KEY=your_finnhub_key

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=pattern
DB_HOST_NAME=db
DB_PORT=5432
```

## Import Conventions

### Old (deprecated)
```python
from plaid_client import plaid_client  # ❌
from utils import sanitize_user         # ❌
```

### New (current)
```python
from integrations.plaid_client import plaid_client  # ✅
from core.utils import sanitize_user                # ✅
```

## Adding New Features

### Adding a New Route
1. Create file in `routes/` (e.g., `routes/new_feature.py`)
2. Define blueprint and endpoints
3. Register blueprint in `app.py`

### Adding a New Integration
1. Create client in `integrations/` (e.g., `integrations/alpha_vantage_client.py`)
2. Use singleton pattern for connection pooling
3. Export from `integrations/__init__.py`

### Adding a New Job
1. Create script in `jobs/` (e.g., `jobs/backfill_data.py`)
2. Use Flask app context for database access
3. Implement logging and error handling
4. Add cron entry or run manually

## Database Migrations

Using Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

```bash
pytest
```

## Logging

All modules use Python's `logging` module:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Information message")
logger.error("Error message")
```

## Architecture Principles

1. **Separation of Concerns**: Routes handle HTTP, services handle logic
2. **Singleton Clients**: Reuse connections for external APIs
3. **Error Tracking**: Use deadletter queue for failed operations
4. **Type Safety**: Use type hints where practical
5. **Logging**: Comprehensive logging for debugging
6. **Modularity**: Clear folder structure for easy navigation

## Contributing

When adding code:
- Follow existing patterns
- Add docstrings to functions
- Update this README if adding new folders
- Test your changes
- Update requirements.txt if adding dependencies
