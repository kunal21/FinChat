# Pattern Finance Dashboard

A personal finance dashboard that lets users link their bank accounts via Plaid and view consolidated assets, accounts, and transaction history in a modern, containerized stack.

---

## Features

- **Account Linking**: Securely connect bank accounts using the Plaid Python SDK.
- **Dashboard Views**: Consolidated view of assets, accounts, and transactions with real-time updates via WebSockets.
- **RESTful API**: Backend built with Python Flask using modular Blueprints and an application-factory pattern.
- **Database Management**: PostgreSQL schema managed by SQLAlchemy ORM and Flask-Migrate for versioned migrations.
- **Containerization**: Entire stack (Flask API, React frontend, PostgreSQL) orchestrated with Docker Compose.

---

## Architecture

```
+-------------+       +-------------+       +------------+
|   React     | <-->  |  Flask API  | <-->  | PostgreSQL |
|  Frontend   |       |  Backend    |       |  Database  |
+-------------+       +-------------+       +------------+
        ^                    ^                    ^
        |                    |                    |
        |    Socket.IO       |                    |
        +--------------------+                    |
        |                                         |
    Docker Compose orchestration                  |
        |                                         |
        +-----------------------------------------+
                     Named volumes
```

---

## Tech Stack

- **Frontend**: React, Axios, `socket.io-client`
- **Backend**: Python 3.11, Flask, Flask-SocketIO, Flask-CORS
- **Database**: PostgreSQL 11.2
- **ORM & Migrations**: SQLAlchemy, Flask-Migrate (Alembic)
- **Containerization**: Docker, Docker Compose
- **Configuration**: python-dotenv for local `.env` loading

---

## Prerequisites

- Docker Engine & Docker Compose installed on host machine
- Plaid developer account credentials (Sandbox or Production)

---

## Environment Variables

Create a `.env` file in the project root (same level as `docker-compose.yml`) with the following:

```dotenv
# Postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=postgres
PLAID_ENV=sandbox
PLAID_CLIENT_ID=<your_plaid_client_id>
PLAID_SECRET=<your_plaid_secret>
```

---

## Setup & Usage

Clone the repository:

```bash
git clone [https://github.com/kunal21/FinChat.git](https://github.com/kunal21/FinChat.git)
cd FinChat
```

Start the application:

```bash
make start
```

This will:

1. Pull or build the Docker images for the client, server, and database.
2. Launch services in detached mode:
   - React frontend on `http://localhost:3001`
   - Flask API on `http://localhost:5001`
   - PostgreSQL on port `5432`
3. Run database migrations automatically via Flask-Migrate.

View logs:

```bash
make logs
```

Stop and clean up:

```bash
make stop
```

---

## API Endpoints

- **Auth**
  - `POST /sessions` – login or register user
- **Users**
  - `GET  /users`        – list all users
  - `POST /users`        – create a new user
  - `GET  /users/:id`    – get user by ID
- **Assets**
  - `GET    /assets/:userId` – list assets for a user
  - `POST   /assets`         – add a new asset
  - `DELETE /assets/:id`     – delete an asset
- **Items / Plaid**
  - `POST   /items`                 – exchange token & add item
  - `POST   /link-token`            – create a Plaid link token
  - `POST   /link-event`            – log link events
- **Accounts & Transactions**
  - `GET /users/:id/accounts`
  - `GET /items/:id/accounts`
  - `GET /users/:id/transactions`
  - `GET /items/:id/transactions`
  - `GET /accounts/:id/transactions`
  - `DELETE /items/:id`

---

## Database Migrations

- Initialize migrations (one-time):
  ```bash
  flask db init
  ```
- Create a new revision after changing models:
  ```bash
  flask db migrate -m "Your message"
  ```
- Apply migrations:
  ```bash
  flask db upgrade
  ```

---

## Development

- React code is live-mounted into the `client` container with `CHOKIDAR_USEPOLLING=true` for reliable hot-reload.
- Flask runs with `FLASK_ENV=development` and auto-reload enabled.
- Use `socket.io` for real-time updates; ensure `setupProxy.js` is configured for `/socket.io` with `ws: true`.

---

