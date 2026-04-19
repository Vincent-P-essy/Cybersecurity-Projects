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
[![Signal Protocol](https://img.shields.io/badge/Signal_Protocol-Double_Ratchet_+_X3DH-3A76F0?style=flat)](https://signal.org/docs/)

> End-to-end encrypted P2P chat implementing the Signal Protocol (Double Ratchet + X3DH key exchange) with WebAuthn/Passkey authentication and zero server-side message storage.

*Security theory, architecture deep-dive, and implementation walkthrough are in the [learn modules](#learn).*

## Security Properties

| Property | Implementation |
|----------|----------------|
| End-to-end encryption | AES-256-GCM via Double Ratchet |
| Key exchange | X3DH (Extended Triple Diffie-Hellman) |
| Forward secrecy | New symmetric key derived per message |
| Break-in recovery | Ratchet reset after detected compromise |
| Authentication | WebAuthn / FIDO2 Passkeys (no passwords) |
| Out-of-order messages | Skipped-key cache up to 1000 messages |

## Features

- **Double Ratchet** — each message encrypted with a fresh symmetric key derived from the ratchet chain; compromise of one key never reveals past or future messages
- **X3DH** — asynchronous key exchange so Alice can send Bob a message even if Bob is offline
- **WebAuthn Passkeys** — phishing-resistant authentication with discoverable credentials, supports multi-device enrollment
- **Real-time WebSocket** with SurrealDB live queries for presence, typing indicators, and read receipts
- **Zero plaintext at rest** — the server stores only encrypted ciphertext and public keys

## Quick Start

```bash
docker compose up -d
# → http://localhost:8080
```

> [!TIP]
> Uses [`just`](https://github.com/casey/just) — run `just` to list all commands.
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Key Exchange Flow (X3DH)

```
Bob publishes to server:
  IK_B  (identity key)
  SPK_B (signed prekey)
  OPK_B (one-time prekey)

Alice fetches Bob's keys → derives shared secret SK:
  SK = KDF(DH(IK_A, SPK_B) || DH(EK_A, IK_B) || DH(EK_A, SPK_B) || DH(EK_A, OPK_B))

Double Ratchet starts from SK — new key per message from here.
```

## Stack

**Backend:** FastAPI, PostgreSQL + SQLModel, SurrealDB, Redis, Alembic

**Frontend:** SolidJS 1.9, TypeScript, Vite 6, Tailwind CSS v4

## Learn

| Module | Topic |
|--------|-------|
| [00 - Overview](learn/00-OVERVIEW.md) | Prerequisites and quick start |
| [01 - Concepts](learn/01-CONCEPTS.md) | Cryptography theory — Diffie-Hellman, ratchets, forward secrecy |
| [02 - Architecture](learn/02-ARCHITECTURE.md) | System design and key management |
| [03 - Implementation](learn/03-IMPLEMENTATION.md) | Protocol implementation walkthrough |
| [04 - Challenges](learn/04-CHALLENGES.md) | Extension ideas and exercises |

## License

AGPL 3.0
