# 02 — Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
│                                                             │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │  PostgreSQL   │    │         Backend (FastAPI)        │  │
│  │  port 5432    │◄───│                                  │  │
│  └──────────────┘    │  ┌─────────┐  ┌──────────────┐   │  │
│                       │  │ SSH HP  │  │   HTTP HP    │   │  │
│                       │  │ :2222   │  │   :8088      │   │  │
│                       │  └─────────┘  └──────────────┘   │  │
│                       │        ┌──────────────┐           │  │
│                       │        │   FTP HP     │           │  │
│                       │        │   :2121      │           │  │
│                       │        └──────────────┘           │  │
│                       │                                   │  │
│                       │  REST API + SSE   :8000           │  │
│                       └──────────────────────────────────┘  │
│                                    ▲                        │
│  ┌──────────────┐                  │ proxy /api/            │
│  │  Frontend    │──────────────────┘                       │
│  │  Nginx :80   │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
         ▲ :8080           ▲ :22 :21 :80
         │                 │
      Browser           Attackers
```

## Data Flow

1. Attacker connects to port 22 / 21 / 80 (mapped to backend honeypot services)
2. Honeypot service logs credentials/commands + emits fake response
3. `_save_event()` persists to PostgreSQL and calls `broadcaster.broadcast()`
4. `broadcaster.broadcast()` pushes the event to all SSE subscriber queues
5. Dashboard `EventSource` receives the push, updates React state instantly
6. Stats endpoint queries PostgreSQL aggregations on demand (polled every 15s)

## Component Responsibilities

### `core/broadcaster.py`
In-memory pub/sub using `asyncio.Queue`. Each SSE connection subscribes a new queue; `broadcast()` fans out to all live subscribers. Dead/full queues are pruned automatically.

### `core/geoip.py`
Async HTTP lookup to `ip-api.com` with an in-process dict cache. Private IP ranges short-circuit to avoid external calls. Rate limit: ip-api.com allows 45 requests/minute on the free tier.

### `core/patterns.py`
Regex-based threat scoring. No ML — pure pattern matching for speed and auditability. Returns `(score, tags)` where tags drive MITRE ATT&CK annotations.

### `honeypots/ssh.py`
Uses `asyncssh` library. Accepts all credentials (`validate_password` always returns `True`), then spawns a `FakeShell` session. The fake shell maps ~15 common commands to realistic responses; everything else returns `command not found`. Commands are logged asynchronously to avoid blocking the SSH handler.

### `honeypots/ftp.py`
Pure asyncio `Protocol` implementation — no third-party FTP library. Handles USER, PASS, LIST, PWD, CWD, RETR (denied), STOR (denied), QUIT. Shows a fake directory listing with enticing filenames (`database_dump.sql`, `.htpasswd`).

### `honeypots/http.py`
`aiohttp` server on a separate port. Serves a fake admin login page mimicking a generic CMS. Pattern-scores every request body and path. All POST submissions (credential attempts) are logged. Known scanner paths (`/wp-admin`, `/.env`, `/.git/config`) are redirected to the login page to maximize engagement.

## Database Schema

```sql
CREATE TABLE honeypot_events (
    id           SERIAL PRIMARY KEY,
    service      VARCHAR   NOT NULL,  -- 'ssh' | 'http' | 'ftp'
    source_ip    VARCHAR   NOT NULL,
    source_port  INTEGER,
    username     VARCHAR,
    password     VARCHAR,
    command      TEXT,
    path         TEXT,
    user_agent   TEXT,
    country      VARCHAR,
    city         VARCHAR,
    threat_score INTEGER DEFAULT 0,
    raw_data     TEXT,
    created_at   TIMESTAMPTZ DEFAULT now()
);
```

## Concurrency Model

All three honeypot services and the FastAPI application share the **same asyncio event loop**. There is no threading — I/O concurrency is achieved entirely through `async/await`. This means:
- Honeypot handlers never block each other
- Database writes are non-blocking (asyncpg)
- SSE stream is non-blocking (async generator)
- A single Python process handles thousands of concurrent honeypot connections
