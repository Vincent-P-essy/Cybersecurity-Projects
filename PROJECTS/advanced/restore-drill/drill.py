"""Create authenticated SQLite snapshots and rehearse their restoration."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import shutil
import sqlite3
import stat
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

MAX_MANIFEST = 1_048_576
DEFAULT_MAX_DATABASE = 268_435_456


class VerificationError(ValueError):
    pass


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def validate_key(key: bytes):
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("Use a signing key of at least 32 bytes")


@contextmanager
def database(path: Path):
    connection = sqlite3.connect(path.resolve(strict=True).as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA trusted_schema=OFF")
        yield connection
    finally:
        connection.close()


def inventory(connection: sqlite3.Connection) -> dict:
    schema = connection.execute("""
        SELECT type, name, tbl_name, sql FROM sqlite_master
        WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name
    """).fetchall()
    tables = {}
    for kind, name, _, _ in schema:
        if kind == "table":
            quoted = '"' + name.replace('"', '""') + '"'
            tables[name] = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
    return {"schema_sha256": hashlib.sha256(canonical(schema)).hexdigest(), "table_rows": tables}


def backup(source: Path, bundle: Path, key: bytes) -> dict:
    validate_key(key)
    if source.is_symlink() or not source.is_file():
        raise ValueError("Source must be a regular database file")
    bundle.mkdir(mode=0o700, parents=False, exist_ok=False)
    try:
        snapshot = bundle / "snapshot.sqlite"
        with database(source) as original:
            destination = sqlite3.connect(snapshot)
            try:
                original.backup(destination)
            finally:
                destination.close()
        snapshot.chmod(0o600)
        with database(snapshot) as restored:
            if restored.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise VerificationError("Source snapshot failed integrity check")
            details = inventory(restored)
        digest = hashlib.sha256()
        with snapshot.open("rb") as stream:
            for block in iter(lambda: stream.read(65536), b""):
                digest.update(block)
        manifest = {"version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                    "database": "snapshot.sqlite", "bytes": snapshot.stat().st_size,
                    "sha256": digest.hexdigest(), **details}
        signature = hmac.new(key, canonical(manifest), hashlib.sha256).hexdigest()
        manifest_path = bundle / "manifest.json"
        manifest_path.write_bytes(canonical({"manifest": manifest, "signature": signature}) + b"\n")
        manifest_path.chmod(0o600)
        for path in (snapshot, manifest_path):
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
        descriptor = os.open(bundle, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return manifest
    except Exception:
        shutil.rmtree(bundle)
        raise


def read_regular(path: Path, limit: int) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise VerificationError("Expected a bounded regular file")
        result = stream.read(limit + 1)
        if len(result) > limit:
            raise VerificationError("File exceeds configured size limit")
        return result


def verify(bundle: Path, key: bytes, checks: list[dict] | None = None,
           *, max_database: int = DEFAULT_MAX_DATABASE) -> dict:
    validate_key(key)
    if bundle.is_symlink() or not bundle.is_dir():
        raise VerificationError("Bundle must be a directory")
    if max_database < 1:
        raise ValueError("Invalid database limit")
    started = time.perf_counter()
    try:
        envelope = json.loads(read_regular(bundle / "manifest.json", MAX_MANIFEST))
        if not isinstance(envelope, dict) or set(envelope) != {"manifest", "signature"}:
            raise VerificationError("Invalid manifest envelope")
        manifest, received = envelope["manifest"], envelope["signature"]
        expected = hmac.new(key, canonical(manifest), hashlib.sha256).hexdigest()
        if not isinstance(received, str) or not hmac.compare_digest(expected, received):
            raise VerificationError("Manifest authentication failed")
        fields = {"version", "created_at", "database", "bytes", "sha256", "schema_sha256", "table_rows"}
        if not isinstance(manifest, dict) or set(manifest) != fields or type(manifest["version"]) is not int or manifest["version"] != 1:
            raise VerificationError("Unsupported manifest")
        if manifest["database"] != "snapshot.sqlite":
            raise VerificationError("Invalid snapshot name")
        if type(manifest["bytes"]) is not int or not 0 < manifest["bytes"] <= max_database:
            raise VerificationError("Snapshot exceeds configured limit")
        for field in ("sha256", "schema_sha256"):
            if not isinstance(manifest[field], str) or not re.fullmatch(r"[0-9a-f]{64}", manifest[field]):
                raise VerificationError("Invalid manifest digest")
        payload = read_regular(bundle / "snapshot.sqlite", max_database)
        if len(payload) != manifest["bytes"] or not hmac.compare_digest(hashlib.sha256(payload).hexdigest(), manifest["sha256"]):
            raise VerificationError("Snapshot bytes do not match authenticated manifest")
        with tempfile.TemporaryDirectory(prefix="restore-drill-") as directory:
            restored_path = Path(directory) / "restored.sqlite"
            restored_path.write_bytes(payload)
            restored_path.chmod(0o600)
            with database(restored_path) as restored:
                if restored.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                    raise VerificationError("Restored database failed integrity check")
                details = inventory(restored)
                if any(details[field] != manifest[field] for field in details):
                    raise VerificationError("Restored inventory differs from manifest")
                results = []
                allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                           sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
                restored.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK
                                        if action in allowed else sqlite3.SQLITE_DENY)
                for check in checks or []:
                    if set(check) != {"name", "sql", "expected"} or not isinstance(check["sql"], str):
                        raise VerificationError("Invalid business check")
                    budget = [0]

                    def progress():
                        budget[0] += 1
                        return int(budget[0] > 10000)

                    restored.set_progress_handler(progress, 100)
                    cursor = restored.execute(check["sql"])
                    row = cursor.fetchone()
                    extra = cursor.fetchone()
                    restored.set_progress_handler(None, 0)
                    if row is None or len(row) != 1 or extra is not None or row[0] != check["expected"]:
                        raise VerificationError(f"Business check failed: {check['name']}")
                    results.append({"name": check["name"], "status": "passed"})
        return {"status": "passed", "database_bytes": len(payload), **details,
                "business_checks": results, "restore_seconds": round(time.perf_counter() - started, 6)}
    except (OSError, sqlite3.Error, ValueError, TypeError, KeyError, RecursionError) as failure:
        if isinstance(failure, VerificationError):
            raise
        raise VerificationError("Restore verification failed") from failure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("backup")
    create.add_argument("source", type=Path)
    create.add_argument("bundle", type=Path)
    rehearse = commands.add_parser("verify")
    rehearse.add_argument("bundle", type=Path)
    rehearse.add_argument("--checks", type=Path)
    args = parser.parse_args()
    try:
        key = bytes.fromhex(os.environ.get("RESTORE_SIGNING_KEY", ""))
        if args.command == "backup":
            result = backup(args.source, args.bundle, key)
        else:
            checks = json.loads(args.checks.read_text()) if args.checks else None
            result = verify(args.bundle, key, checks)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError) as failure:
        parser.exit(1, f"{failure}\n")


if __name__ == "__main__":
    main()
