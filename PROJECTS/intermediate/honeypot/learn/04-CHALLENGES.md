# 04 — Challenges

## Beginner

**1. Add a Telnet honeypot**
Implement a `honeypots/telnet.py` using the same asyncio `Protocol` pattern as FTP. Telnet runs on port 23 and is extremely common in IoT botnet scanning. Add it to `main.py` and `compose.yml`.

**2. Expand SSH command coverage**
Add 20 more realistic command responses to `_RESPONSES` in `ssh.py`. Include: `cat /proc/cpuinfo`, `free -h`, `df -h`, `last`, `who`, `iptables -L`, `crontab -l`.

**3. Country flag in the dashboard**
Use the `countryCode` field (already stored) to display emoji flags in the EventFeed table. ISO 3166-1 alpha-2 codes map to flags via Unicode regional indicator symbols.

## Intermediate

**4. Webhook alerting**
Add a `WEBHOOK_URL` config option. When an event with `threat_score >= 70` is captured, POST it to the webhook. Use this to send Slack or Discord notifications on high-threat events.

**5. Rate limiting detection**
Track connection frequency per IP in Redis. If an IP connects more than 5 times in 60 seconds, mark all its events as `brute_force=True` and increase the threat score. This is exactly how Fail2Ban detects brute forces.

**6. Integrate with the SIEM dashboard**
The SIEM project (`intermediate/siem-dashboard`) accepts log ingestion. Write an adapter that converts Canaris events to the SIEM log format and POST them to its ingestion endpoint. This gives you correlation rules across multiple data sources.

**7. Persistent SSH session logging**
Currently, each command is a separate DB event. Implement session grouping — assign a `session_id` to each SSH connection and store all commands from that session under the same ID. Add a "Session detail" view in the dashboard.

## Advanced

**8. High-interaction SSH with Docker isolation**
Replace the fake bash shell with a real restricted container. When an attacker authenticates, spawn a Docker container (using the Docker SDK) with no network access and record everything using `strace` or `eBPF`. This is how modern high-interaction honeypots work.

**9. TLS/SSL decoy**
Add an HTTPS honeypot on port 443 using a self-signed certificate. Many scanners probe HTTPS endpoints. Log the TLS handshake details (cipher suites, SNI hostname) to fingerprint the scanner tool.

**10. Threat intelligence export**
Implement a `GET /api/export/iocs` endpoint that returns a list of attacker IPs in STIX 2.1 format. This is the industry standard for sharing threat intelligence. Automate submission to a public TI feed like AbuseIPDB.

**11. Machine learning anomaly detection**
Instead of (or alongside) regex patterns, train a `scikit-learn` Isolation Forest on normal HTTP request patterns, then score new requests by their anomaly distance. Compare precision/recall with the regex approach. For inspiration, look at the `advanced/ai-threat-detection` project in this repo.

## Research Questions

- What is the ratio of automated scans vs. human-operated attacks in your deployment data?
- Which credentials appear most frequently? Does it match known leaked password lists (RockYou, LinkedIn breach)?
- At what time of day are most attacks observed? Does this correlate with timezone data from the GeoIP?
- How long does an attacker spend in the fake SSH shell before giving up?
