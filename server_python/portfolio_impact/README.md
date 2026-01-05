# Portfolio Impact System

Analyzes news and market events to assess their impact on user portfolios and generates personalized notifications.

## Structure

```
portfolio_impact/
├── clients/              # Data source integrations
│   └── finnhub_client.py     # Finnhub news API client
├── analyzers/            # Impact analysis engines
│   └── impact_analyzer.py    # LLM-based materiality analyzer
└── jobs/                 # Batch processing scripts
    └── batch_job.py          # Main news ingestion job
```

## Components

### Clients (`clients/`)
Data source clients for fetching financial news and market data.

- **finnhub_client.py**: Fetches company news from Finnhub API
  - `finnhub_fetch()` - Retrieves news for a ticker
  - `parse_finnhub_article()` - Normalizes API response

**Future additions**: Alpha Vantage, Polygon.io, etc.

### Analyzers (`analyzers/`)
Analysis engines that assess impact and materiality of news events.

- **impact_analyzer.py**: LLM-powered materiality analysis
  - `analyze_impact_with_retry()` - Determines if news is material to ticker
  - Returns: impact_level, impact_summary, estimated_effect, confidence

**Future additions**: Sentiment analysis, risk scoring, etc.

### Jobs (`jobs/`)
Batch jobs and scheduled tasks for processing.

- **batch_job.py**: Main ingestion pipeline
  - Fetches news for all user holdings
  - Analyzes materiality with LLM
  - Creates UserImpact notifications
  - Logs metrics and errors

**Future additions**: Scheduled cron jobs, backfill scripts, etc.

## Usage

### Running the Batch Job

**Inside Docker (recommended):**

```bash
# 1. Set up environment (one time)
echo "FINNHUB_API_KEY=your_key" >> .env

# 2. Make sure services are running
docker compose up -d

# 3. Run the batch job inside the server container
docker compose exec server python portfolio_impact/jobs/batch_job.py
```

**Local development (requires local Python setup):**

```bash
# Only if you have all dependencies installed locally
cd server_python
python portfolio_impact/jobs/batch_job.py
```

## Data Flow

1. **Fetch** → Clients retrieve news from external APIs
2. **Store** → Articles saved to database with ticker association
3. **Analyze** → Analyzers determine materiality and impact level
4. **Notify** → UserImpact records created for affected users
5. **UI** → Frontend displays impacts to users

## Database Models

- **Article**: News articles with ticker, title, url, published_at, is_material
- **UserImpact**: User notifications with impact_level, summary, estimated_effect
- **Holding**: User portfolio holdings with ticker_symbol
- **Deadletter**: Failed operations for debugging

## Adding New Features

### Adding a New Data Source

1. Create `clients/new_source_client.py`
2. Implement `fetch()` and `parse()` functions
3. Add exports to `clients/__init__.py`
4. Update batch job to use new client

### Adding a New Analyzer

1. Create `analyzers/new_analyzer.py`
2. Implement analysis logic with retry/validation
3. Add exports to `analyzers/__init__.py`
4. Integrate into batch job pipeline

### Adding a New Job

1. Create `jobs/new_job.py`
2. Follow batch_job.py patterns for:
   - Flask app context
   - Logging
   - Error handling with deadletter
   - Metrics tracking
3. Make executable with `if __name__ == "__main__":`

## Configuration

Environment variables in `server_python/.env`:

```bash
# Required
FINNHUB_API_KEY=your_finnhub_key
OPENAI_CLIENT_ID=your_openai_key

# Optional
LLM_MODEL=gpt-4o-mini
```

## Logging

All jobs log to stdout with format:
```
YYYY-MM-DD HH:MM:SS [LEVEL] message
```

Levels:
- **INFO**: Progress, metrics, successful operations
- **DEBUG**: Detailed debug information
- **ERROR**: Failures, exceptions
