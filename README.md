# FinChat - AI-Powered Portfolio Impact Notifications

AI-powered platform that monitors financial news and alerts you to events affecting your investments. Get personalized notifications before the market moves.

## Features

* **Portfolio Impact Intelligence:** Auto-monitor news for your holdings, AI analyzes materiality, personalized alerts (HIGH/MEDIUM/LOW)
* **Conversational AI Assistant:** Ask natural-language questions about your finances
* **Secure Bank Integration:** Connect accounts via Plaid for automatic sync
* **Containerized Deployment:** Docker-based with hot-reload for development

## Tech Stack

* **Frontend:** React, TypeScript
* **Backend:** Flask (Python), PostgreSQL
* **APIs:** OpenAI (GPT-4o-mini), Plaid (banking), Finnhub (news)
* **Deployment:** Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API Keys: OpenAI, Plaid, Finnhub

### Setup

```bash
# Clone and navigate
git clone https://github.com/kunal21/FinChat.git
cd FinChat/pattern

# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Start services
docker compose up --build
```

**Access at:**

- Client: <http://localhost:3001>
- Server API: <http://localhost:5001>

## Usage

### Run News Ingestion

```bash
# Fetch latest news for all user holdings
docker compose exec server python portfolio_impact/jobs/batch_job.py

# Update transactions from Plaid
docker compose exec server python jobs/update_transactions.py
```

### Common Commands

```bash
# View logs
docker compose logs --follow

# Stop services
docker compose down

# Access database
docker compose exec db psql -U postgres
```

## Project Structure

```
pattern/
├── client/                     # React frontend
├── server_python/              # Flask backend
│   ├── portfolio_impact/       # News ingestion & AI analysis
│   ├── routes/                 # API endpoints
│   ├── models/                 # Database models
│   └── integrations/           # External APIs (Plaid, OpenAI, Finnhub)
└── docker-compose.yml
```

See [CLAUDE.md](CLAUDE.md) for detailed architecture and [server_python/README.md](server_python/README.md) for backend documentation.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Built by Kunal Mehta
