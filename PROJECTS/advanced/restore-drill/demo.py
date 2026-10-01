import json
import secrets
import sqlite3
import tempfile
from pathlib import Path

from drill import VerificationError, backup, verify


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source, bundle = root / "source.sqlite", root / "backup"
        connection = sqlite3.connect(source)
        connection.executescript("CREATE TABLE invoices(id INTEGER PRIMARY KEY, cents INTEGER); INSERT INTO invoices VALUES(1,1500);")
        connection.close()
        key = secrets.token_bytes(32)
        backup(source, bundle, key)
        source.unlink()
        checks = [{"name": "invoice total", "sql": "SELECT SUM(cents) FROM invoices", "expected": 1500}]
        print("Original fixture removed; restoring only from the snapshot")
        print(json.dumps(verify(bundle, key, checks), indent=2))
        snapshot = bundle / "snapshot.sqlite"
        payload = bytearray(snapshot.read_bytes())
        payload[-1] ^= 1
        snapshot.write_bytes(payload)
        try:
            verify(bundle, key, checks)
        except VerificationError:
            print("Altered snapshot: rejected")


if __name__ == "__main__":
    main()
