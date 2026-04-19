![Author](https://img.shields.io/badge/Author-Vincent%20Plessy-blue)

<p align="center">
  <p>Cybersecurity Projects</p>
</p>

```ruby
██████╗ ██╗   ██╗ ██████╗     ██████╗  ██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗
██╔══██╗██║   ██║██╔════╝     ██╔══██╗██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝
██████╔╝██║   ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║██╔██╗ ██║   ██║    ╚████╔╝
██╔══██╗██║   ██║██║   ██║    ██╔══██╗██║   ██║██║   ██║██║╚██╗██║   ██║     ╚██╔╝
██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║   ██║      ██║
╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝      ╚═╝
```

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Live Demo](https://img.shields.io/badge/Live-bugbounty.Vincent--P--essy.com-green?style=flat&logo=googlechrome)](https://bugbounty.Vincent-P-essy.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker)](https://www.docker.com)

> Production-ready enterprise bug bounty platform. ~7,000 lines of backend across three role types, CVSS scoring, full report triage, and bounty award workflows with complete audit logging.

*Security theory, architecture deep-dive, and implementation walkthrough are in the [learn modules](#learn).*

## Features

- **3-role RBAC** — Researcher, Company, Admin with JWT refresh token rotation and multi-device session management
- **CVSS v3.1 scoring** — full vector string calculation with severity breakdown
- **Report lifecycle** — submit → triage → validate → reward → close with SLA tracking
- **Program management** — configurable scope (in-scope/out-of-scope assets), reward tiers per severity
- **Audit logging** — every state change recorded with actor, timestamp, and reason
- **Security hardened** — Argon2id password hashing, rate limiting, input validation, SQL injection prevention via SQLAlchemy ORM

## Preview

![Bug Bounty Platform](docs/screenshots/dashboard.png)

## Demo

Live instance: **[bugbounty.Vincent-P-essy.com](https://bugbounty.Vincent-P-essy.com/)**

| Role | Email | Password |
|------|-------|----------|
| Researcher | `researcher@demo.com` | `Demo1234!` |
| Company | `company@demo.com` | `Demo1234!` |
| Admin | `admin@demo.com` | `Demo1234!` |

Or run locally:

```bash
docker compose up -d
# → http://localhost:8420
```

> [!TIP]
> Uses [`just`](https://github.com/casey/just) — run `just` to list all commands.
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Report Lifecycle

```
Researcher submits report
        ↓
Company triages (needs_more_info / accepted / rejected)
        ↓
Company validates (confirmed / not_reproducible / duplicate)
        ↓
Admin awards bounty (based on CVSS severity + program tier)
        ↓
Report closed → audit log entry created
```

## Stack

**Backend:** FastAPI, SQLAlchemy 2.0, PostgreSQL 18, Redis 7, Alembic, Argon2id, JWT (~7,000 lines)

**Frontend:** React 19, TypeScript 5.9, Vite 7, React Router 7.1, TanStack Query v5, Zustand

## Learn

| Module | Topic |
|--------|-------|
| [00 - Overview](learn/00-OVERVIEW.md) | Prerequisites and quick start |
| [01 - Concepts](learn/01-CONCEPTS.md) | Bug bounty programs and vulnerability disclosure |
| [02 - Architecture](learn/02-ARCHITECTURE.md) | System design and data flow |
| [03 - Implementation](learn/03-IMPLEMENTATION.md) | Code walkthrough |
| [04 - Challenges](learn/04-CHALLENGES.md) | Extension ideas and exercises |

## License

AGPL 3.0
