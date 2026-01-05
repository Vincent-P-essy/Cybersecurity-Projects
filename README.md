![Author](https://img.shields.io/badge/Author-Vincent%20Plessy-blue)
[![Lint & Type Check](https://github.com/Vincent-P-essy/Cybersecurity-Projects/actions/workflows/lint.yml/badge.svg)](https://github.com/Vincent-P-essy/Cybersecurity-Projects/actions/workflows/lint.yml)

<p align="center">
  <h1 align="center">👨‍💻 Vincent Plessy</h1>
  <p align="center"><strong>Cybersecurity • Systems • DevOps</strong></p>

  <img src="https://img.shields.io/badge/Linux-✔-blue">
  <img src="https://img.shields.io/badge/Security-✔-red">
  <img src="https://img.shields.io/badge/DevOps-✔-orange">
  <img src="https://img.shields.io/badge/Projects-✔-green">

  <br>

  <img src="https://img.shields.io/github/stars/Vincent-P-essy/Cybersecurity-Projects?style=social">
  <img src="https://img.shields.io/github/forks/Vincent-P-essy/Cybersecurity-Projects?style=social">
</p>

<p align="center">
  💼 Open to Cybersecurity / DevOps Apprenticeship
</p>

---

## 👨‍💻 About Me

Computer Science student (L3) passionate about cybersecurity, systems, and low-level programming.

- 🎯 Goal: Cybersecurity / DevOps apprenticeship
- 🧠 Interests: Offensive security, defensive systems, infrastructure
- ⚙️ Strong focus on practical, real-world projects

---

## 🚀 Featured Projects

### 🤖 AI Threat Detection
[➡️ View Project](./PROJECTS/advanced/ai-threat-detection)

ML-powered threat detection engine analyzing nginx logs in real time with a 3-model ensemble (Autoencoder + Random Forest + Isolation Forest). Detects SQLi, XSS, path traversal, Log4Shell, and SSRF. Auto-trains on deployment.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

### 🐛 Bug Bounty Platform
[➡️ View Project](./PROJECTS/advanced/bug-bounty-platform) • [🌐 Live Demo](https://bugbounty.Vincent-P-essy.com)

Production-ready enterprise bug bounty platform with RBAC (Researcher / Company / Admin), CVSS scoring, report triage, bounty award workflows, and full audit logging. ~7,000 lines of backend.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

### 🔒 Encrypted P2P Chat
[➡️ View Project](./PROJECTS/advanced/encrypted-p2p-chat)

End-to-end encrypted peer-to-peer chat implementing the Signal Protocol (Double Ratchet + X3DH). WebAuthn/Passkey authentication, forward secrecy, break-in recovery, real-time WebSocket messaging.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![SolidJS](https://img.shields.io/badge/SolidJS-2C4F7C?style=flat&logo=solid&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

### 📊 SIEM Dashboard
[➡️ View Project](./PROJECTS/intermediate/siem-dashboard) • [🌐 Live Demo](https://siem.Vincent-P-essy.com)

Full-stack SIEM with real-time log correlation, three rule types (Threshold, Sequence, Aggregation), four MITRE ATT&CK attack playbooks, and a live alert feed via Server-Sent Events.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

### 🍯 Canaris — Honeypot
[➡️ View Project](./PROJECTS/intermediate/honeypot)

Multi-service honeypot emulating SSH, HTTP, and FTP to capture attacker credentials and commands in real time. Threat scoring 0–100 with MITRE ATT&CK pattern mapping, GeoIP enrichment, and a live React dashboard.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

## 📂 All Projects

### 🟢 Beginner

| Project | Description | Tech |
|---------|-------------|------|
| [Base64 Tool](./PROJECTS/beginner/base64-tool) | Multi-format encoding/decoding CLI with auto-detection and recursive peel | Python |
| [Caesar Cipher](./PROJECTS/beginner/caesar-cipher) | Encrypt, decrypt, and brute-force crack with frequency analysis | Python |
| [Hash Cracker](./PROJECTS/beginner/hash-cracker) | Multi-threaded dictionary + brute-force cracker (MD5, SHA1, SHA256, SHA512) | C++ |
| [DNS Lookup](./PROJECTS/beginner/dns-lookup) | Professional DNS query CLI with WHOIS integration and batch queries | Python |
| [Simple Port Scanner](./PROJECTS/beginner/simple-port-scanner) | Asynchronous TCP scanner with configurable concurrency | C++ |
| [Network Traffic Analyzer](./PROJECTS/beginner/network-traffic-analyzer) | Dual implementation packet analyzer with real-time TUI | C++ / Python |
| [C2 Beacon](./PROJECTS/beginner/c2-beacon) | Command & Control system with WebSocket protocol and operator dashboard | Python / React |
| [Keylogger](./PROJECTS/beginner/keylogger) | Cross-platform educational keylogger with log rotation and window tracking | Python |
| [Metadata Scrubber](./PROJECTS/beginner/metadata-scrubber-tool) | Privacy-focused CLI stripping metadata from JPEG, PDF, Office files | Python |
| [Firewall Rule Engine](./PROJECTS/beginner/firewall-rule-engine) | iptables/nftables rule parser with conflict detection and optimizer | V |
| [Linux CIS Auditor](./PROJECTS/beginner/linux-cis-hardening-auditor) | 104-control CIS Benchmark compliance auditor with HTML/JSON reports | Bash |
| [Vulnerability Scanner](./PROJECTS/beginner/simple-vulnerability-scanner) | Python dependency updater with CVE detection via OSV.dev | Go |

### 🟡 Intermediate

| Project | Description | Tech |
|---------|-------------|------|
| [API Security Scanner](./PROJECTS/intermediate/api-security-scanner) | OWASP API Top 10 scanner with React dashboard and scan history | Python / React |
| [Binary Analysis Tool](./PROJECTS/intermediate/binary-analysis-tool) [![Live](https://img.shields.io/badge/Live-axumortem-green?style=flat)](https://axumortem.Vincent-P-essy.com) | ELF/PE/Mach-O static analyzer with YARA scanning and threat scoring | Rust / React |
| [Canaris Honeypot](./PROJECTS/intermediate/honeypot) | SSH + HTTP + FTP honeypot with live threat dashboard | Python / React |
| [Docker Security Audit](./PROJECTS/intermediate/docker-security-audit) | CIS Docker Benchmark v1.6.0 auditor with SARIF/JUnit output | Go |
| [SBOM Generator](./PROJECTS/intermediate/sbom-generator-vulnerability-matcher) | SPDX/CycloneDX SBOM generator with OSV + NVD vulnerability matching | Go |
| [Secrets Scanner](./PROJECTS/intermediate/secrets-scanner) | 150-rule secrets scanner with Shannon entropy and HIBP breach verification | Go |
| [SIEM Dashboard](./PROJECTS/intermediate/siem-dashboard) [![Live](https://img.shields.io/badge/Live-siem-green?style=flat)](https://siem.Vincent-P-essy.com) | Real-time SIEM with log correlation and MITRE ATT&CK playbooks | Python / React |
| [Credential Enumeration](./PROJECTS/intermediate/credential-enumeration) | Post-access credential exposure detector for Linux systems | Nim |

### 🔴 Advanced

| Project | Description | Tech |
|---------|-------------|------|
| [AI Threat Detection](./PROJECTS/advanced/ai-threat-detection) | 3-model ML ensemble for real-time nginx log threat detection | Python / PyTorch / React |
| [API Rate Limiter](./PROJECTS/advanced/api-rate-limiter) | Enterprise FastAPI rate limiter (Sliding Window, Token Bucket, Fixed Window) | Python |
| [Bug Bounty Platform](./PROJECTS/advanced/bug-bounty-platform) [![Live](https://img.shields.io/badge/Live-bugbounty-green?style=flat)](https://bugbounty.Vincent-P-essy.com) | Full bug bounty platform with RBAC, CVSS scoring, and audit logging | Python / React |
| [Encrypted P2P Chat](./PROJECTS/advanced/encrypted-p2p-chat) | Signal Protocol (Double Ratchet + X3DH) P2P chat with WebAuthn | Python / SolidJS |
| [Reverse Proxy](./PROJECTS/advanced/haskell-reverse-proxy) | High-performance reverse proxy with security middleware | Haskell |

---

## 🛠️ Tech Stack

![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Nim](https://img.shields.io/badge/Nim-FFE953?style=for-the-badge&logo=nim&logoColor=black)
![Haskell](https://img.shields.io/badge/Haskell-5D4F85?style=for-the-badge&logo=haskell&logoColor=white)

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

---

## 📊 Stats

![Repo Size](https://img.shields.io/github/repo-size/Vincent-P-essy/Cybersecurity-Projects)
![Last Commit](https://img.shields.io/github/last-commit/Vincent-P-essy/Cybersecurity-Projects)
![Language](https://img.shields.io/github/languages/top/Vincent-P-essy/Cybersecurity-Projects)

---

## 📫 Contact

- 📧 Email: vincent.plessy12@gmail.com
- 💻 GitHub: https://github.com/Vincent-P-essy
