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

[![Cybersecurity Projects](https://img.shields.io/badge/Cybersecurity--Projects-Project%20%2325-red?style=flat&logo=github)](https://github.com/Vincent-P-essy/Cybersecurity-Projects/tree/main/PROJECTS/intermediate/honeypot)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker)](https://www.docker.com)

> Medium-interaction honeypot emulating SSH, HTTP, and FTP servers concurrently. Captures attacker credentials, commands, and TTPs in real time with automatic MITRE ATT&CK annotation and a live React dashboard.

*Security theory, architecture deep-dive, and implementation walkthrough are in the [learn modules](#learn).*

## Features

- **3 concurrent honeypot services** running inside a single asyncio event loop — zero threading overhead
- **SSH fake shell** — accepts all credentials, responds to ~15 recon commands with realistic Ubuntu output
- **HTTP fake admin panel** — mimics a generic CMS, detects SQLi / XSS / path traversal / LFI patterns
- **FTP decoy server** — exposes a fake directory with enticing filenames (`database_dump.sql`, `.htpasswd`)
- **Threat scoring 0–100** — every event is scored at capture time using regex-based pattern analysis
- **MITRE ATT&CK mapping** — techniques automatically annotated from observed behavior
- **GeoIP enrichment** — country, city, ISP via ip-api.com with in-memory caching
- **Live dashboard** via Server-Sent Events — events appear in real time, no polling
- **Statistics panel** — top IPs, most-used credentials, attack breakdown by country and service

## Quick Start

```bash
docker compose up -d
```

Dashboard → `http://localhost:8080`

> [!WARNING]
> Deploy on a dedicated internet-facing VPS for real-world captures. Never run honeypots on a production network.

> [!TIP]
> Uses [`just`](https://github.com/casey/just) as task runner — run `just` to list all commands.
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Threat Scoring

| Behavior | Score |
|----------|-------|
| Connection alone | +5 |
| Default credentials (`root/admin/admin`) | +20 |
| Scanner user-agent (Nikto, sqlmap, Masscan) | +25 |
| SQL injection pattern in path or body | +40 |
| Path traversal (`../`, `/etc/passwd`) | +35 |
| SSH dangerous command (`wget`, `curl`, `nc`, `base64`) | +50 |
| SSH credential access (`/etc/shadow`, `.ssh/authorized_keys`) | +30 |

## MITRE ATT&CK Mapping

| Observed Behavior | Technique |
|-------------------|-----------|
| SSH brute force credential collection | T1110 — Brute Force |
| `crontab`, `rc.local` via SSH | T1053 — Scheduled Task/Job |
| `wget` / `curl` via SSH | T1105 — Ingress Tool Transfer |
| `/etc/passwd`, `.ssh/authorized_keys` read | T1003 — OS Credential Dumping |
| HTTP `.env` access | T1552.001 — Credentials In Files |
| HTTP path traversal | T1083 — File and Directory Discovery |

## Architecture

```
Internet → :22 / :21 / :80
                ↓
   ┌────────────┬─────────────┬────────────┐
   │  SSH HP    │   HTTP HP   │   FTP HP   │
   │ (asyncssh) │  (aiohttp)  │  (asyncio) │
   └────────────┴─────────────┴────────────┘
                ↓  same event loop
        _save_event() → PostgreSQL
                ↓
        broadcaster.broadcast()
                ↓
    FastAPI SSE /api/events/stream
                ↓
         React Dashboard
```

## Stack

**Backend:** Python 3.13, FastAPI, asyncssh, aiohttp, SQLAlchemy async, asyncpg

**Frontend:** React 19, TypeScript, Vite, Recharts

**Data:** PostgreSQL 17

## Honeypot Services

| Service | Port | Simulates |
|---------|------|-----------|
| SSH | 22 | Ubuntu 22.04 interactive bash shell |
| HTTP | 80 | Generic CMS admin panel + scanner path traps |
| FTP | 21 | Linux FTP server with fake sensitive files |

## Learn

| Module | Topic |
|--------|-------|
| [00 - Overview](learn/00-OVERVIEW.md) | Prerequisites and quick start |
| [01 - Concepts](learn/01-CONCEPTS.md) | Honeypot theory and deception technology |
| [02 - Architecture](learn/02-ARCHITECTURE.md) | System design and data flow |
| [03 - Implementation](learn/03-IMPLEMENTATION.md) | Code walkthrough |
| [04 - Challenges](learn/04-CHALLENGES.md) | Extension ideas and exercises |

## License

AGPL 3.0
