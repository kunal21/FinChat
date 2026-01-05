# FinChat - AI-Powered Portfolio Impact Notifications

A real-time portfolio intelligence platform that analyzes financial news and alerts you to events that could impact your investments. Know what matters to your portfolio before the market moves.

## 🎯 Core Features

### Portfolio Impact Intelligence
* **Real-Time News Analysis:** Automatically monitors financial news for all your holdings using Finnhub API
* **AI-Powered Materiality Assessment:** GPT-4 analyzes each article to determine if it's material to your specific holdings
* **Personalized Impact Notifications:** Get alerts tailored to your portfolio with impact level (HIGH/MEDIUM/LOW), estimated effect (positive/negative), and AI-generated summaries
* **Smart Deduplication:** Canonical URL matching ensures you never see the same news twice
* **Interactive Dashboard:** View, filter, and manage your portfolio impact notifications with real-time updates

### Additional Features
* **Conversational AI Assistant:** Ask natural-language questions about your finances using GPT-4 and RAG
* **Secure Bank Integration:** Connect accounts via Plaid API for automatic transaction and holdings sync
* **Comprehensive Analytics:** Track net worth, spending patterns, and investment performance
* **Containerized Architecture:** Production-ready Docker deployment with hot-reload for development

## 🚀 How It Works

1. **Connect Your Accounts** → Link investment accounts securely through Plaid
2. **Automatic Monitoring** → System continuously fetches news for your holdings from Finnhub
3. **AI Analysis** → GPT-4 evaluates each article's materiality and potential impact on your positions
4. **Get Alerted** → Receive personalized notifications ranked by impact level with AI-generated summaries
5. **Take Action** → Read full articles, ask FinChat AI questions, or dismiss irrelevant updates

## 🛠️ Tech Stack

* **Frontend:** React, TypeScript, TailwindCSS
* **Backend:** Python (Flask), OpenAI API (GPT-4), Plaid API, Finnhub API
* **AI & NLP:** GPT-4 for materiality analysis, impact assessment, and conversational AI
* **Database:** PostgreSQL with JSONB for structured analysis storage
* **Containerization:** Docker Compose for multi-service orchestration

## 📦 Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- API Keys: OpenAI, Plaid, Finnhub

### 1. Clone the repository

```bash
git clone https://github.com/kunal21/FinChat.git
cd FinChat/pattern
```

### 2. Set up environment variables

```bash
cp .env.template .env
```

Edit `.env` and add your API keys:
```bash
# Required
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET_SANDBOX=your_plaid_sandbox_secret
OPENAI_CLIENT_ID=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=postgres
```

### 3. Build and run with Docker Compose

```bash
# Start all services (db, server, ngrok, client)
docker compose up --build

# Or run in detached mode
docker compose up --build -d

# Wait for services to initialize (optional - runs automatically)
./wait-for-client.sh
```

The application will be available at:
- **Client**: http://localhost:3001
- **Server API**: http://localhost:5001
- **Ngrok Dashboard**: http://localhost:4040 (for webhook testing)

## 🎯 Usage

### Accessing Portfolio Impact

1. Open http://localhost:3001 in your browser
2. Create an account or log in
3. Connect your investment accounts securely using Plaid
4. Click the **"Portfolio Impact"** tab to view your personalized alerts
5. Each impact card shows:
   - **What happened**: News headline and source
   - **Why it affects you**: AI-generated explanation of materiality
   - **Estimated impact**: Predicted effect (positive/negative/neutral)
   - **Actions**: Read full article, ask AI, mark as read, or dismiss

### Running News Ingestion

The system can run as a manual batch job or scheduled via cron:

```bash
# Manual run: Fetch latest news for all user holdings
docker compose exec server python portfolio_impact/jobs/batch_job.py

# Schedule with cron (example: every 4 hours)
0 */4 * * * docker compose exec server python portfolio_impact/jobs/batch_job.py
```

### Additional Features

**Financial Chat Assistant:**
- Click the **"FinChat"** tab
- Ask questions like:
  - "How much did I spend on groceries last month?"
  - "What's my current net worth?"
  - "Analyze my investment returns this quarter"

**Transaction Sync:**
```bash
# Update transactions from Plaid for all users
docker compose exec server python jobs/update_transactions.py
```

### Docker Compose Commands

```bash
# View logs
docker compose logs --follow

# View logs for specific service
docker compose logs --follow server

# Stop all services
docker compose down

# Stop and remove volumes (clears database)
docker compose down -v

# Restart a specific service
docker compose restart server

# List running services
docker compose ps

# Access database
docker compose exec db psql -U postgres

# Run batch jobs
docker compose exec server python portfolio_impact/jobs/batch_job.py
```

### Running in Debug Mode

```bash
# Use debug configuration with hot-reload
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
```

## 📁 Project Structure

See [server_python/README.md](server_python/README.md) for detailed backend documentation.

```
pattern/
├── client/                     # React TypeScript frontend
│   ├── src/components/
│   │   ├── PortfolioImpact.tsx # Impact notifications UI
│   │   ├── ChatWindow.tsx      # AI chat interface
│   │   └── ...
│   └── src/services/
│       └── api.tsx             # API client functions
│
├── server_python/              # Flask Python backend
│   ├── portfolio_impact/       # Portfolio impact intelligence system
│   │   ├── clients/            # News API clients (Finnhub)
│   │   │   └── finnhub_client.py
│   │   ├── analyzers/          # AI analysis engines
│   │   │   └── impact_analyzer.py
│   │   └── jobs/               # Batch processing jobs
│   │       └── batch_job.py
│   │
│   ├── integrations/           # External API clients
│   │   ├── plaid_client.py     # Plaid banking integration
│   │   ├── openai_client.py    # OpenAI embeddings & LLM
│   │   └── data/
│   │
│   ├── routes/                 # API endpoints
│   │   ├── users.py            # User & impacts endpoints
│   │   ├── accounts.py         # Account management
│   │   ├── messages.py         # Chat messages
│   │   └── ...
│   │
│   ├── models/                 # Database models
│   │   ├── user_impact.py      # Portfolio impact notifications
│   │   ├── article.py          # News articles
│   │   ├── holding.py          # Investment holdings
│   │   └── ...
│   │
│   ├── news_ingestion/         # News processing utilities
│   │   ├── util.py             # URL canonicalization, text cleanup
│   │   └── pipeline.py         # Deduplication, error handling
│   │
│   └── core/                   # Core utilities
│       └── utils.py            # Data serializers
│
├── ngrok/                      # Webhook tunnel configuration
├── docker-compose.yml          # Production services
├── docker-compose.debug.yml    # Debug configuration
└── .env                        # Environment variables
```

## 🔧 Development

### Making Code Changes

Changes are automatically reflected due to volume mounts in docker-compose:
- **Server**: Edit files in `server_python/` - Flask auto-reloads
- **Client**: Edit files in `client/` - React hot-reloads

### Running Batch Jobs

```bash
# Finnhub news ingestion
docker compose exec server python portfolio_impact/jobs/batch_job.py

# Update transactions from Plaid
docker compose exec server python jobs/update_transactions.py
```

### Database Migrations

```bash
# Access database shell
docker compose exec db psql -U postgres

# Run migrations (if using Alembic)
docker compose exec server alembic upgrade head
```

### Adding New Features

See detailed guides in:
- Backend: [server_python/README.md](server_python/README.md)
- Portfolio Impact System: [server_python/portfolio_impact/README.md](server_python/portfolio_impact/README.md)

## 🔍 How Portfolio Impact Works

### News Ingestion Pipeline

1. **Ticker Discovery**
   - Query all unique ticker symbols from user holdings
   - Filter out empty/invalid tickers

2. **News Fetching**
   - For each ticker, fetch last 24 hours of news from Finnhub API
   - Parse article metadata (title, summary, source, published date)

3. **Deduplication**
   - Canonicalize URLs (remove UTM params, normalize)
   - Check if article already exists in database
   - Skip duplicates to avoid redundant processing

4. **AI Materiality Analysis**
   - Send article text + ticker to GPT-4
   - Prompt asks: "Is this material for {ticker}?"
   - Returns structured JSON:
     ```json
     {
       "is_material": true,
       "impact_level": "HIGH|MEDIUM|LOW",
       "impact_summary": "1-2 sentence explanation",
       "estimated_effect": "positive|negative|neutral",
       "confidence": 0.85
     }
     ```

5. **User Impact Generation**
   - If article is material (is_material=true):
     - Find all users holding that ticker
     - Create one UserImpact record per user
     - Store impact level, summary, and effect
   - If not material: Store article but don't create impacts

6. **Metrics & Logging**
   - Track: articles fetched, inserted, skipped, analyzed
   - Log: material articles identified, impacts created
   - Error handling: Failed operations go to deadletter table

### Frontend Display

1. **Data Fetching**
   - On mount: GET `/users/{userId}/impacts`
   - Returns impacts with embedded article details
   - Sorted by creation date (newest first)

2. **Impact Cards**
   - Header: Ticker + impact level badge (color-coded)
   - What happened: Article title + source
   - Why it matters: AI-generated impact summary
   - Estimated impact: Positive/negative/neutral effect

3. **User Actions**
   - Read full article: Opens source URL in new tab
   - Mark as read: PATCH with `{read: true}`
   - Dismiss: PATCH with `{dismissed: true}` (removes from list)

4. **Live Stats**
   - Active alerts: Count of non-dismissed impacts
   - Coverage: Unique tickers with impacts
   - Updated: Time since most recent impact

## 🎨 Customization

### Adjust News Timeframe

Edit [batch_job.py](server_python/portfolio_impact/jobs/batch_job.py):
```python
# Change from last 24 hours to last 7 days
from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
```

### Change Impact Threshold

Edit [impact_analyzer.py](server_python/portfolio_impact/analyzers/impact_analyzer.py) prompt to adjust materiality criteria.

### Add New News Sources

1. Create new client in `portfolio_impact/clients/`
2. Implement `fetch()` and `parse()` functions
3. Update batch job to use new source

## ✅ Future Enhancements

* **Automated Scheduling**: Cron job for continuous news monitoring
* **Email/SMS Alerts**: Push notifications for high-impact events
* **Portfolio Correlation Analysis**: Identify sector-wide impacts
* **Historical Impact Tracking**: Measure prediction accuracy over time
* **Custom Alert Rules**: User-defined impact thresholds and filters
* **Multi-Source Aggregation**: Combine Finnhub, NewsAPI, Alpha Vantage
* **Sentiment Analysis**: Track sentiment trends for holdings
* **Mobile Application**: iOS/Android apps with push notifications

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Built by Kunal Mehta
