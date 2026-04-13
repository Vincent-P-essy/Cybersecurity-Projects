# 00 — Overview

## What You Will Learn

- How honeypots work as deception-based detection systems
- Implementing fake network services using asyncio and asyncssh
- Real-time event streaming with Server-Sent Events (SSE)
- Threat scoring using pattern detection and MITRE ATT&CK mapping
- IP geolocation enrichment for attacker attribution

## Prerequisites

| Skill | Level |
|-------|-------|
| Python async/await | Intermediate |
| TCP/IP networking basics | Beginner |
| SQL and SQLAlchemy | Beginner |
| React + TypeScript | Beginner |
| Docker Compose | Beginner |

## Quick Start

```bash
# Clone and start
git clone https://github.com/Vincent-P-essy/cybersecurity-projects
cd PROJECTS/intermediate/honeypot
docker compose up -d

# Watch the event stream
just stream

# See stats
just stats
```

Dashboard: `http://localhost:8080`

## Project Structure

```
honeypot/
├── backend/
│   └── app/
│       ├── honeypots/     # ssh.py, ftp.py, http.py
│       ├── api/           # events.py, stats.py (FastAPI routes)
│       └── core/          # broadcaster.py, geoip.py, patterns.py
├── frontend/
│   └── src/
│       └── components/    # EventFeed.tsx, StatsPanel.tsx
├── compose.yml
└── justfile
```

## Learning Path

1. **[01 - Concepts](01-CONCEPTS.md)** — Understand what honeypots are and why they work
2. **[02 - Architecture](02-ARCHITECTURE.md)** — How the components fit together
3. **[03 - Implementation](03-IMPLEMENTATION.md)** — Deep dive into the code
4. **[04 - Challenges](04-CHALLENGES.md)** — Extend the project yourself
