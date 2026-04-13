# 03 — Implementation

## SSH Honeypot Deep Dive

The SSH server uses `asyncssh`, which abstracts the SSH protocol and exposes clean Python hooks.

```python
class _SSHHoneypotServer(asyncssh.SSHServer):

    def password_auth_supported(self) -> bool:
        return True  # advertise password auth

    async def validate_password(self, username: str, password: str) -> bool:
        # Always accept — log the credentials first
        asyncio.create_task(_save_event(ip, port, username, password))
        return True  # ← attacker gets a shell

    def session_requested(self) -> asyncssh.SSHServerSession:
        return _FakeShell(self._username, *self._peer)
```

Key insight: `validate_password` always returns `True`. This maximises credential collection — if we rejected credentials, automated scanners would move on immediately.

### Fake Shell

```python
class _FakeShell(asyncssh.SSHServerSession):
    def data_received(self, data: str, datatype):
        self._buf += data
        if "\n" not in self._buf:
            return  # wait for full line

        cmd = self._buf.strip()
        response = _RESPONSES.get(cmd, f"bash: {cmd.split()[0]}: command not found")
        self._chan.write(response + "\nroot@prod-server:~# ")
        asyncio.create_task(_save_event(..., command=cmd))
```

`_RESPONSES` is a dict mapping ~15 common reconnaissance commands (`id`, `whoami`, `ls`, `cat /etc/passwd`, `ps aux`, `history`…) to plausible Ubuntu output. Unknown commands get a `bash: not found` response, which is realistic.

## FTP Honeypot Deep Dive

```python
class _FTPSession(asyncio.Protocol):
    def data_received(self, data: bytes):
        line = data.decode(errors="replace").strip()
        cmd, arg = line.split(None, 1) if " " in line else (line, "")
        cmd = cmd.upper()

        if cmd == "USER":
            self._username = arg
            self._send("331 Password required.")
        elif cmd == "PASS":
            asyncio.create_task(_save_event(..., username=self._username, password=arg))
            self._send("230 Login successful.")
        elif cmd == "LIST":
            self._send("150 Here comes the directory listing.")
            self._send(_FAKE_LISTING)   # includes .htpasswd, db dump
            self._send("226 Directory send OK.")
```

The FTP protocol is line-oriented and stateful. We implement the minimal command set needed to fool automated scanners: `USER`, `PASS`, `LIST`, `PWD`, `CWD`, `RETR` (fails), `STOR` (fails), `PASV`, `QUIT`.

## HTTP Honeypot Deep Dive

```python
async def _handle_post(req: web.Request) -> web.Response:
    data = await req.post()
    username = str(data.get("username", ""))
    password = str(data.get("password", ""))
    body = f"username={username}&password={password}"

    score, tags = score_http_request(req.path, body, ua)
    asyncio.create_task(_save_event(..., threat_score=score))

    return web.Response(text=_LOGIN_PAGE.format(
        error='<p class="error">Invalid credentials.</p>'
    ))
```

The HTTP honeypot **never succeeds** (always returns "Invalid credentials") — but it does respond with a realistic HTML page so scanners keep probing.

Pattern detection in `core/patterns.py`:

```python
_SQLI_PATTERNS = re.compile(
    r"('|--|union\s+select|select\s+.*from|drop\s+table)", re.IGNORECASE
)

def score_http_request(path, body, user_agent) -> tuple[int, list[str]]:
    score = 5
    tags = []
    if _SQLI_PATTERNS.search(path) or _SQLI_PATTERNS.search(body):
        score += 40
        tags.append("sqli")
    ...
    return min(score, 100), tags
```

## Event Broadcasting (SSE)

```python
# broadcaster.py
_subscribers: Set[asyncio.Queue] = set()

async def broadcast(data: dict):
    for q in _subscribers.copy():
        try:
            q.put_nowait(data)       # non-blocking
        except asyncio.QueueFull:
            _subscribers.discard(q)  # drop dead clients

# events.py — SSE endpoint
async def stream_events():
    q = subscribe()
    async def _generator():
        try:
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"   # keep connection alive
        finally:
            unsubscribe(q)
    return StreamingResponse(_generator(), media_type="text/event-stream")
```

The SSE format is two newlines after each `data:` line. The periodic ping prevents proxies from closing idle connections.

## GeoIP Enrichment

```python
async def lookup_ip(ip: str) -> dict:
    if ip in _cache:
        return _cache[ip]                  # hot path, no I/O

    if _is_private(ip):
        return {"country": "Private", ...} # LAN, never external

    async with httpx.AsyncClient(timeout=3.0) as client:
        resp = await client.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()
        ...
    _cache[ip] = result
    return result
```

The cache is unbounded but grows slowly (one entry per unique attacker IP). For production deployments with millions of events, replace with a bounded LRU cache or Redis.

## React SSE Integration

```typescript
export function openEventStream(onEvent: (e: HoneypotEvent) => void): EventSource {
  const es = new EventSource(`/api/events/stream`);
  es.onmessage = (msg) => {
    try {
      onEvent(JSON.parse(msg.data));
    } catch { /* ping comment lines */ }
  };
  return es;
}

// In EventFeed.tsx:
useEffect(() => {
  const es = openEventStream((ev) => {
    setEvents((prev) => [ev, ...prev.slice(0, 199)]);  // keep 200 in memory
  });
  return () => es.close();  // cleanup on unmount
}, []);
```

`EventSource` is a native browser API — no library needed. It automatically reconnects on disconnect.
