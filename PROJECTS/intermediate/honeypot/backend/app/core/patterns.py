import re

_SQLI_PATTERNS = re.compile(
    r"('|--|;|\/\*|\*\/|union\s+select|select\s+.*from|insert\s+into|drop\s+table|xp_cmdshell)",
    re.IGNORECASE,
)
_XSS_PATTERNS = re.compile(r"(<script|javascript:|onerror=|onload=|<iframe|alert\()", re.IGNORECASE)
_TRAVERSAL_PATTERNS = re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%252e)", re.IGNORECASE)
_SCANNER_AGENTS = re.compile(
    r"(nikto|sqlmap|nmap|masscan|zgrab|nuclei|dirbuster|gobuster|hydra|metasploit|burpsuite|acunetix)",
    re.IGNORECASE,
)
_CMD_INJECTION = re.compile(r"(;|\||&&|\$\(|`)\s*(ls|cat|id|whoami|wget|curl|bash|sh|python|nc\s)", re.IGNORECASE)

_SSH_DANGEROUS_CMDS = re.compile(
    r"(wget|curl|chmod\s+[0-7]{3,4}|python.*-c|bash\s+-[ic]|nc\s+-[elp]|/dev/tcp|base64\s+-d|perl\s+-e)",
    re.IGNORECASE,
)


def score_http_request(path: str, body: str, user_agent: str) -> tuple[int, list[str]]:
    score = 5
    tags: list[str] = []

    if _SQLI_PATTERNS.search(path) or _SQLI_PATTERNS.search(body):
        score += 40
        tags.append("sqli")
    if _XSS_PATTERNS.search(path) or _XSS_PATTERNS.search(body):
        score += 30
        tags.append("xss")
    if _TRAVERSAL_PATTERNS.search(path):
        score += 35
        tags.append("path-traversal")
    if _SCANNER_AGENTS.search(user_agent):
        score += 25
        tags.append("scanner")
    if _CMD_INJECTION.search(path) or _CMD_INJECTION.search(body):
        score += 45
        tags.append("cmd-injection")

    return min(score, 100), tags


def score_ssh_command(command: str) -> tuple[int, list[str]]:
    score = 10
    tags: list[str] = []

    if _SSH_DANGEROUS_CMDS.search(command):
        score += 50
        tags.append("malicious-command")
    if re.search(r"(passwd|shadow|sudoers|\.ssh/authorized_keys)", command):
        score += 30
        tags.append("credential-access")
    if re.search(r"(crontab|systemctl|service\s+.*start|rc\.local)", command):
        score += 25
        tags.append("persistence")

    return min(score, 100), tags
