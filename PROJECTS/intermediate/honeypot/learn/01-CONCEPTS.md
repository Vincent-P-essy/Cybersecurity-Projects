# 01 — Concepts

## What Is a Honeypot?

A honeypot is a decoy system designed to attract attackers. It looks like a legitimate target but serves no production purpose — any interaction with it is inherently suspicious.

```
Real infrastructure:  [Web Server] [DB Server] [API Server]
Honeypot:             [Fake SSH]   [Fake FTP]  [Fake Admin Panel]
                            ↑
                    Attacker wastes time here while you observe
```

## Types of Honeypots

| Type | Description | Use Case |
|------|-------------|----------|
| **Low-interaction** | Simulates services without a real OS | Credential collection, scanning detection |
| **High-interaction** | Full OS, real software | Deep attacker behavior analysis |
| **Medium-interaction** | Fake shell, believable responses | Balance between safety and intel |
| **Honeynets** | Network of multiple honeypots | Large-scale threat intelligence |

Canaris implements **medium-interaction** honeypots — the services are fake but respond realistically enough to keep attackers engaged.

## Why Attackers Fall for Honeypots

Attackers scan the internet automatically (Shodan, Masscan, ZGrab). A port being open is enough to trigger automated exploitation scripts. Honeypots exploit this automation — the attacker's tools don't distinguish between real and fake services.

Common automated attacks Canaris catches:
- SSH brute force (Mirai, Medusa, Hydra)
- FTP credential stuffing
- WordPress admin panel scanning
- `.env` file exposure attempts
- phpMyAdmin default credential attacks
- SQL injection probing

## Threat Scoring (0–100)

Every event receives a threat score based on the observed behavior:

| Behavior | Score Contribution |
|----------|--------------------|
| Connection alone | +5–10 |
| Common default credentials (root/admin) | +20 |
| Scanner user-agent (Nikto, sqlmap) | +25 |
| SQL injection pattern in request | +40 |
| Path traversal attempt | +35 |
| Dangerous SSH command (wget, curl, nc, base64) | +50 |
| Credential/persistence access in SSH | +25–30 |

## MITRE ATT&CK Mapping

| Honeypot Action | ATT&CK Technique |
|-----------------|------------------|
| SSH brute force credential collection | T1110 — Brute Force |
| SSH command: `crontab`, `rc.local` | T1053 — Scheduled Task/Job |
| SSH command: `wget`/`curl` | T1105 — Ingress Tool Transfer |
| SSH read `/etc/passwd`, `.ssh/authorized_keys` | T1003 — OS Credential Dumping |
| HTTP `.env` access | T1552.001 — Credentials In Files |
| HTTP path traversal | T1083 — File and Directory Discovery |

## Legal and Ethical Considerations

> [!WARNING]
> Honeypots must be deployed responsibly.

- **Deploy in isolation** — never on a production network; a compromised honeypot can pivot to real systems
- **Inform your ISP** — some providers prohibit honeypot traffic; others require notification
- **No entrapment** — a honeypot captures opportunistic attackers, not lures specific individuals
- **Data retention** — IP addresses and credentials are personal data in many jurisdictions; comply with GDPR/local laws
- **No active countermeasures** — logging is fine; hacking back is illegal in most countries
