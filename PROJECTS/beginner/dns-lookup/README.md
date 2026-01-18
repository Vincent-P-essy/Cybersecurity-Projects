![Author](https://img.shields.io/badge/Author-Vincent%20Plessy-blue)


<p align="center">
  <p>Cybersecurity Projects</p>
</p>


```ruby
██████╗ ███╗   ██╗███████╗██╗      ██████╗  ██████╗ ██╗  ██╗██╗   ██╗██████╗
██╔══██╗████╗  ██║██╔════╝██║     ██╔═══██╗██╔═══██╗██║ ██╔╝██║   ██║██╔══██╗
██║  ██║██╔██╗ ██║███████╗██║     ██║   ██║██║   ██║█████╔╝ ██║   ██║██████╔╝
██║  ██║██║╚██╗██║╚════██║██║     ██║   ██║██║   ██║██╔═██╗ ██║   ██║██╔═══╝
██████╔╝██║ ╚████║███████║███████╗╚██████╔╝╚██████╔╝██║  ██╗╚██████╔╝██║
╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝
```

[![Cybersecurity Projects](https://img.shields.io/badge/Cybersecurity--Projects-Project%20%234-red?style=flat&logo=github)](https://github.com/Vincent-P-essy/Cybersecurity-Projects/tree/main/PROJECTS/beginner/dns-lookup)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PyPI](https://img.shields.io/pypi/v/dnslookup-cli?color=3775A9&logo=pypi&logoColor=white)](https://pypi.org/project/dnslookup-cli/)
[![Publish](https://github.com/Vincent-P-essy/Cybersecurity-Projects/actions/workflows/publish-dns-lookup.yml/badge.svg)](https://github.com/Vincent-P-essy/Cybersecurity-Projects/actions/workflows/publish-dns-lookup.yml)

> Professional DNS query CLI with Rich terminal output, reverse lookups, and WHOIS integration.

*This is a quick overview — security theory, architecture, and full walkthroughs are in the [learn modules](#learn).*

## What It Does

- Query A, AAAA, MX, NS, TXT, CNAME, and SOA records with colored table output
- Reverse DNS lookup to resolve IP addresses back to hostnames
- Trace DNS resolution path from root servers to authoritative nameservers
- Batch lookups with concurrent queries for processing domain lists
- WHOIS integration for domain registration information
- JSON export for scripting and pipeline integration

## Quick Start

```bash
uv tool install dnslookup-cli
dnslookup query example.com
```

> [!TIP]
> This project uses [`just`](https://github.com/casey/just) as a command runner. Type `just` to see all available commands.
>
> Install: `curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin`

## Commands

| Command | Description |
|---------|-------------|
| `dnslookup query` | Query DNS records for a domain with colored table output |
| `dnslookup reverse` | Resolve an IP address back to its hostname |
| `dnslookup trace` | Trace the DNS resolution path from root to authoritative servers |
| `dnslookup batch` | Query multiple domains concurrently from a file |
| `dnslookup whois` | Retrieve WHOIS registration information for a domain |

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
