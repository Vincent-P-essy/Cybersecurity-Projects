![Author](https://img.shields.io/badge/Author-Vincent%20Plessy-blue)


<p align="center">
  <p>Cybersecurity Projects</p>
</p>


```ruby
██████╗ ██████╗ ██████╗      ██████╗██╗  ██╗ █████╗ ████████╗
██╔══██╗╚════██╗██╔══██╗    ██╔════╝██║  ██║██╔══██╗╚══██╔══╝
██████╔╝ █████╔╝██████╔╝    ██║     ███████║███████║   ██║
██╔═══╝ ██╔═══╝ ██╔═══╝     ██║     ██╔══██║██╔══██║   ██║
██║     ███████╗██║         ╚██████╗██║  ██║██║  ██║   ██║
╚═╝     ╚══════╝╚═╝          ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
```

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![SolidJS](https://img.shields.io/badge/SolidJS-1.9-4F88C6?style=flat&logo=solid&logoColor=white)](https://www.solidjs.com)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker)](https://www.docker.com)
[![Signal Protocol](https://img.shields.io/badge/Signal_Protocol-E2EE-3A76F0?style=flat)](https://signal.org/docs/)

> End-to-end encrypted peer-to-peer chat with Signal Protocol (Double Ratchet + X3DH) and WebAuthn/Passkey authentication.

*This is a quick overview — security theory, architecture, and full walkthroughs are in the [learn modules](#learn).*

## What It Does

- Double Ratchet protocol (Signal) with X3DH key exchange for end-to-end encryption
- WebAuthn/Passkey authentication with discoverable credentials and multi-device support
- Forward secrecy and break-in recovery with out-of-order message handling
- Real-time WebSocket messaging with SurrealDB live queries
- Presence tracking, typing indicators, read receipts, and heartbeat keep-alive
- Alembic database migrations with full test suite

## Quick Start

```bash
docker compose up -d
```

Visit `http://localhost:8080` to open the application.

> [!TIP]
> This project uses [`just`](https://github.com/casey/just) as a command runner. Type `just` to see all available commands.
>
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Stack

**Backend:** FastAPI, PostgreSQL + SQLModel, SurrealDB, Redis, Alembic

**Frontend:** SolidJS 1.9, TypeScript, Vite 6, Tailwind CSS v4

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
