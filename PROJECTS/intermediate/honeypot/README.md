![Author](https://img.shields.io/badge/Author-Vincent%20Plessy-blue)


<p align="center">
  <p>Cybersecurity Projects</p>
</p>


```ruby
 ██████╗ █████╗ ███╗   ██╗ █████╗ ██████╗ ██╗███████╗
██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗██║██╔════╝
██║     ███████║██╔██╗ ██║███████║██████╔╝██║███████╗
██║     ██╔══██║██║╚██╗██║██╔══██║██╔══██╗██║╚════██║
╚██████╗██║  ██║██║ ╚████║██║  ██║██║  ██║██║███████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
```

[![Cybersecurity Projects](https://img.shields.io/badge/Cybersecurity--Projects-Project%20%2325-red?style=flat&logo=github)](https://github.com/Vincent-P-essy/cybersecurity-projects/tree/main/PROJECTS/intermediate/honeypot)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker)](https://www.docker.com)

> Multi-service honeypot that emulates SSH, HTTP, and FTP servers to capture attacker credentials, commands, and techniques in real time.

*This is a quick overview — security theory, architecture, and full walkthroughs are in the [learn modules](#learn).*

## What It Does

- Three concurrent honeypot services: SSH (fake interactive bash shell), HTTP (fake admin panel detecting SQLi/XSS/path traversal), FTP (fake file server capturing credentials)
- Every event is scored 0–100 using pattern analysis (MITRE ATT&CK techniques mapped to threat score)
- Real-time dashboard via Server-Sent Events — see attacks as they happen
- GeoIP enrichment for every attacker IP (country, city)
- Statistics panel: top attacking IPs, most-used credentials, countries, attack breakdown by service
- Single `docker compose up` deployment — exposes ports 22, 21, 80 as honeypots and port 8080 as the dashboard

## Quick Start

```bash
docker compose up -d
```

Visit `http://localhost:8080` for the live dashboard.

> [!WARNING]
> Deploy on an internet-facing server (VPS) to capture real-world attacks. Never run honeypots on a production network without isolation.

> [!TIP]
> This project uses [`just`](https://github.com/casey/just) as a command runner. Type `just` to see all available commands.
>
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Stack

**Backend:** Python 3.13+, FastAPI, asyncssh, aiohttp, SQLAlchemy (async), asyncpg

**Frontend:** React 19, TypeScript, Vite, Recharts

**Data:** PostgreSQL 17

**Honeypot Services:**

| Service | Port | Simulates |
|---------|------|-----------|
| SSH | 22 | Ubuntu 22.04 with interactive bash shell |
| HTTP | 80 | Generic CMS admin panel, phpMyAdmin, .env exposure |
| FTP | 21 | Linux FTP server with fake sensitive files |

## How It Works

```
Internet → Port 22/21/80 → Honeypot Services (asyncssh / aiohttp / asyncio)
                                    ↓
                           Pattern Analysis + GeoIP
                                    ↓
                            PostgreSQL (events)
                                    ↓
                   FastAPI SSE stream → React Dashboard
```

Each honeypot service is a coroutine running inside the same FastAPI process. When an attacker connects, credentials and commands are logged, enriched with geolocation, scored for threat level, and broadcast to all connected dashboard clients via SSE.

## Learn

This project includes step-by-step learning materials covering security theory, architecture, and implementation.

| Module | Topic |
|--------|-------|
| [00 - Overview](learn/00-OVERVIEW.md) | Prerequisites and quick start |
| [01 - Concepts](learn/01-CONCEPTS.md) | Honeypot theory and deception technology |
| [02 - Architecture](learn/02-ARCHITECTURE.md) | System design and data flow |
| [03 - Implementation](learn/03-IMPLEMENTATION.md) | Code walkthrough |
| [04 - Challenges](learn/04-CHALLENGES.md) | Extension ideas and exercises |

## License

AGPL 3.0
