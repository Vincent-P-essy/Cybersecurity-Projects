"""Signed webhook admission and a transactional, lease-based SQLite outbox."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


class Rejected(ValueError):
    def __init__(self, status: int, reason: str):
        super().__init__(reason)
        self.status = status


@dataclass(frozen=True)
class SigningKey:
    producer: str
    secret: bytes


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value):
        raise Rejected(400, "Invalid identifier")
    return value


def signature(secret: bytes, key_id: str, timestamp: str, event_id: str, body: bytes) -> str:
    envelope = f"webhook-v1\n{key_id}\n{timestamp}\n{event_id}\n".encode("ascii") + body
    return hmac.new(secret, envelope, hashlib.sha256).hexdigest()


def sign(key_id: str, key: SigningKey, event_id: str, body: bytes, now: int) -> dict[str, str]:
    identifier(key_id)
    identifier(event_id)
    timestamp = str(now)
    return {
        "key_id": key_id,
        "event_id": event_id,
        "timestamp": timestamp,
        "signature": signature(key.secret, key_id, timestamp, event_id, body),
    }


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(value: str):
    raise ValueError(f"Invalid JSON constant: {value}")


class Gateway:
    def __init__(self, database: Path, keys: dict[str, SigningKey], *, window: int = 300,
                 max_body: int = 65_536):
        if window < 1 or max_body < 1 or not keys:
            raise ValueError("Invalid configuration")
        self.database = str(database)
        self.keys = dict(keys)
        self.window = window
        self.max_body = max_body
        for key_id, key in self.keys.items():
            identifier(key_id)
            identifier(key.producer)
            if not isinstance(key.secret, bytes) or len(key.secret) < 32:
                raise ValueError("Signing keys must contain at least 32 bytes")
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS inbox (
                    producer TEXT NOT NULL, event_id TEXT NOT NULL,
                    digest TEXT NOT NULL, receipt TEXT NOT NULL,
                    PRIMARY KEY (producer, event_id)
                );
                CREATE TABLE IF NOT EXISTS outbox (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producer TEXT NOT NULL, event_id TEXT NOT NULL, body BLOB NOT NULL,
                    state TEXT NOT NULL DEFAULT 'pending', token TEXT,
                    lease_until INTEGER NOT NULL DEFAULT 0, attempts INTEGER NOT NULL DEFAULT 0,
                    UNIQUE (producer, event_id)
                );
            """)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database, timeout=10)
        try:
            connection.execute("PRAGMA synchronous=FULL")
            with connection:
                yield connection
        finally:
            connection.close()

    def accept(self, headers: dict[str, str], body: bytes, *, now: int | None = None) -> dict:
        now = int(time.time()) if now is None else now
        if not isinstance(body, bytes) or len(body) > self.max_body:
            raise Rejected(413, "Body too large")
        key_id = identifier(headers.get("key_id", ""))
        event_id = identifier(headers.get("event_id", ""))
        timestamp = headers.get("timestamp", "")
        received = headers.get("signature", "")
        if not isinstance(timestamp, str) or not re.fullmatch(r"[0-9]{1,12}", timestamp) or str(int(timestamp)) != timestamp:
            raise Rejected(400, "Invalid timestamp")
        key = self.keys.get(key_id)
        if key is None or not isinstance(received, str) or not re.fullmatch(r"[0-9a-f]{64}", received):
            raise Rejected(401, "Invalid signature")
        expected = signature(key.secret, key_id, timestamp, event_id, body)
        if not hmac.compare_digest(expected, received):
            raise Rejected(401, "Invalid signature")
        if abs(now - int(timestamp)) > self.window:
            raise Rejected(401, "Expired event")
        try:
            payload = json.loads(body.decode("utf-8"), object_pairs_hook=unique_object,
                                 parse_constant=invalid_constant)
        except (ValueError, UnicodeError, RecursionError) as failure:
            raise Rejected(400, "Invalid JSON") from failure
        if not isinstance(payload, dict) or set(payload) != {"type", "data"}:
            raise Rejected(400, "Expected type and data")
        identifier(payload["type"])
        if not isinstance(payload["data"], dict):
            raise Rejected(400, "Expected object data")
        digest = hashlib.sha256(body).hexdigest()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute(
                "SELECT digest, receipt FROM inbox WHERE producer=? AND event_id=?",
                (key.producer, event_id),
            ).fetchone()
            if previous:
                if previous[0] != digest:
                    raise Rejected(409, "Event id reused with different content")
                return {"status": "duplicate", "receipt": previous[1]}
            receipt = uuid.uuid4().hex
            connection.execute("INSERT INTO inbox VALUES (?, ?, ?, ?)",
                               (key.producer, event_id, digest, receipt))
            connection.execute("INSERT INTO outbox (producer, event_id, body) VALUES (?, ?, ?)",
                               (key.producer, event_id, body))
        return {"status": "accepted", "receipt": receipt}

    def claim(self, *, now: int | None = None, lease_seconds: int = 30) -> dict | None:
        now = int(time.time()) if now is None else now
        if not 1 <= lease_seconds <= 3600:
            raise ValueError("Lease must be between 1 and 3600 seconds")
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("""
                SELECT id, producer, event_id, body, attempts FROM outbox
                WHERE state='pending' OR (state='leased' AND lease_until<=?)
                ORDER BY id LIMIT 1
            """, (now,)).fetchone()
            if row is None:
                return None
            token = uuid.uuid4().hex
            connection.execute("""
                UPDATE outbox SET state='leased', token=?, lease_until=?, attempts=attempts+1 WHERE id=?
            """, (token, now + lease_seconds, row[0]))
        return {"id": row[0], "producer": row[1], "event_id": row[2], "body": row[3],
                "attempts": row[4] + 1, "token": token}

    def acknowledge(self, event_id: int, token: str) -> bool:
        with self.connect() as connection:
            result = connection.execute("""
                UPDATE outbox SET state='done', token=NULL
                WHERE id=? AND token=? AND state='leased'
            """, (event_id, token))
            return result.rowcount == 1
