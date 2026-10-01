import hashlib
import hmac
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from drill import VerificationError, backup, canonical, verify


class RestoreTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "source.sqlite"
        self.bundle = self.root / "bundle"
        self.key = bytes(range(32))
        connection = sqlite3.connect(self.source)
        connection.executescript("""
            CREATE TABLE invoices(id INTEGER PRIMARY KEY, cents INTEGER NOT NULL);
            INSERT INTO invoices VALUES(1,1500),(2,2500);
        """)
        connection.close()
        self.checks = [{"name": "invoices total", "sql": "SELECT SUM(cents) FROM invoices", "expected": 4000}]

    def create(self):
        return backup(self.source, self.bundle, self.key)

    def rewrite_manifest(self, mutate):
        path = self.bundle / "manifest.json"
        envelope = json.loads(path.read_bytes())
        mutate(envelope["manifest"])
        envelope["signature"] = hmac.new(self.key, canonical(envelope["manifest"]), hashlib.sha256).hexdigest()
        path.write_bytes(canonical(envelope))

    def test_real_restore_without_source(self):
        self.create()
        self.source.unlink()
        result = verify(self.bundle, self.key, self.checks)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["table_rows"], {"invoices": 2})
        self.assertEqual(result["business_checks"][0]["status"], "passed")

    def test_live_wal_snapshot_includes_committed_data(self):
        connection = sqlite3.connect(self.source)
        self.addCleanup(connection.close)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("INSERT INTO invoices VALUES(3,1000)")
        connection.commit()
        self.create()
        self.assertEqual(verify(self.bundle, self.key)["table_rows"], {"invoices": 3})

    def test_backup_does_not_overwrite_existing_directory(self):
        self.bundle.mkdir()
        marker = self.bundle / "keep.txt"
        marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual(marker.read_text(), "keep")

    def test_tampered_snapshot_rejected(self):
        self.create()
        path = self.bundle / "snapshot.sqlite"
        payload = bytearray(path.read_bytes())
        payload[-1] ^= 1
        path.write_bytes(payload)
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key)

    def test_tampered_manifest_rejected(self):
        self.create()
        path = self.bundle / "manifest.json"
        envelope = json.loads(path.read_bytes())
        envelope["manifest"]["table_rows"]["invoices"] = 0
        path.write_bytes(canonical(envelope))
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key)

    def test_wrong_key_rejected(self):
        self.create()
        with self.assertRaises(VerificationError):
            verify(self.bundle, b"z" * 32)

    def test_schema_mismatch_rejected_even_with_valid_signature(self):
        self.create()
        self.rewrite_manifest(lambda manifest: manifest.update(schema_sha256="0" * 64))
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key)

    def test_business_invariant_failure(self):
        self.create()
        checks = [{**self.checks[0], "expected": 999}]
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key, checks)

    def test_checks_cannot_write_or_attach(self):
        self.create()
        for sql in ["DELETE FROM invoices", f"ATTACH DATABASE '{self.root / 'unwanted.sqlite'}' AS other",
                    "PRAGMA writable_schema=ON"]:
            with self.assertRaises(VerificationError):
                verify(self.bundle, self.key, [{"name": "unsafe", "sql": sql, "expected": None}])
        self.assertFalse((self.root / "unwanted.sqlite").exists())
        self.assertEqual(verify(self.bundle, self.key)["table_rows"], {"invoices": 2})

    def test_scalar_check_must_have_one_row(self):
        self.create()
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key, [{"name": "ambiguous", "sql": "SELECT cents FROM invoices", "expected": 1500}])

    def test_snapshot_symlink_rejected(self):
        self.create()
        snapshot = self.bundle / "snapshot.sqlite"
        snapshot.unlink()
        snapshot.symlink_to(self.source)
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key)

    def test_traversal_name_rejected(self):
        self.create()
        self.rewrite_manifest(lambda manifest: manifest.update(database="../source.sqlite"))
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key)

    def test_size_limit(self):
        self.create()
        with self.assertRaises(VerificationError):
            verify(self.bundle, self.key, max_database=100)

    def test_invalid_source_cleans_partial_bundle(self):
        self.source.write_bytes(b"not a database")
        with self.assertRaises(sqlite3.Error):
            self.create()
        self.assertFalse(self.bundle.exists())

    def test_short_key_rejected(self):
        with self.assertRaises(ValueError):
            backup(self.source, self.bundle, b"short")
        self.assertFalse(self.bundle.exists())


if __name__ == "__main__":
    unittest.main()
