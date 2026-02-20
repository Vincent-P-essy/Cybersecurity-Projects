![Author](https://img.shields.io/badge/Author-Vincent%20Plessy-blue)


<p align="center">
  <p>Cybersecurity Projects</p>
</p>


```ruby
███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
```

[![Cybersecurity Projects](https://img.shields.io/badge/Cybersecurity--Projects-Project%20%231-red?style=flat&logo=github)](https://github.com/Vincent-P-essy/Cybersecurity-Projects/tree/main/PROJECTS/intermediate/api-security-scanner)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker)](https://www.docker.com)
[![OWASP](https://img.shields.io/badge/OWASP-API_Top_10-orange?style=flat)](https://owasp.org/API-Security/)

> Full-stack API vulnerability scanner targeting the OWASP API Security Top 10 with configurable scan modules and a React dashboard.

*This is a quick overview — security theory, architecture, and full walkthroughs are in the [learn modules](#learn).*

## What It Does

- Scans REST APIs against OWASP API Security Top 10 vulnerability categories
- Tests for authentication bypass, injection flaws, IDOR, and rate limiting weaknesses
- SQLi, authentication, IDOR, and rate limit scanner modules with configurable payloads
- JWT auth with bcrypt password hashing and session management
- Scan history tracking with detailed vulnerability reports per endpoint
- Full React dashboard for configuring scans and reviewing results

## Quick Start

```bash
docker compose up -d
```

Visit `http://localhost:8080` to open the dashboard.

> [!TIP]
> This project uses [`just`](https://github.com/casey/just) as a command runner. Type `just` to see all available commands.
>
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, Alembic, httpx, aiohttp

**Frontend:** React, TypeScript, Vite

## Learn

This project includes step-by-step learning materials covering security theory, architecture, and implementation.

| Module | Topic |
|--------|-------|
| [00 - Overview](learn/00-OVERVIEW.md) | Prerequisites and quick start |
| [01 - Concepts](learn/01-CONCEPTS.md) | Security theory and real-world breaches |
| [02 - Architecture](learn/02-ARCHITECTURE.md) | System design and data flow |
| [03 - Implementation](learn/03-IMPLEMENTATION.md) | Code walkthrough |
| [04 - Challenges](learn/04-CHALLENGES.md) | Extension ideas and exercises |


## License

AGPL 3.0
