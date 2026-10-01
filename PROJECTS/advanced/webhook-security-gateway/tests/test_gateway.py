import concurrent.futures
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from gateway import Gateway, Rejected, SigningKey, sign


class GatewayTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "events.sqlite"
        self.old = SigningKey("payments", bytes(range(32)))
        self.new = SigningKey("payments", bytes(range(32, 64)))
        self.gateway = Gateway(self.path, {"old": self.old, "new": self.new})
        self.body = json.dumps({"type": "payment.settled", "data": {"amount_cents": 1500}}).encode()
        self.headers = sign("old", self.old, "evt-1", self.body, 1000)

    def count(self, table):
        with self.gateway.connect() as connection:
            return connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def reject(self, status, headers=None, body=None, now=1000):
        with self.assertRaises(Rejected) as result:
            self.gateway.accept(self.headers if headers is None else headers,
                                self.body if body is None else body, now=now)
        self.assertEqual(result.exception.status, status)

    def test_signed_event_and_duplicate(self):
        first = self.gateway.accept(self.headers, self.body, now=1000)
        second = self.gateway.accept(self.headers, self.body, now=1000)
        self.assertEqual(first["receipt"], second["receipt"])
        self.assertEqual((first["status"], second["status"]), ("accepted", "duplicate"))
        self.assertEqual(self.count("outbox"), 1)

    def test_modified_body(self):
        self.reject(401, body=self.body + b" ")
        self.assertEqual(self.count("inbox"), 0)

    def test_signature_binds_event_and_key(self):
        self.reject(401, headers={**self.headers, "event_id": "evt-2"})
        self.reject(401, headers={**self.headers, "key_id": "new"})
        self.reject(401, headers={**self.headers, "timestamp": "1001"})

    def test_expired_and_future_events(self):
        self.reject(401, now=1301)
        self.reject(401, now=699)
        self.assertEqual(self.gateway.accept(self.headers, self.body, now=1300)["status"], "accepted")

    def test_rotation_does_not_duplicate_business_event(self):
        first = self.gateway.accept(self.headers, self.body, now=1000)
        headers = sign("new", self.new, "evt-1", self.body, 1010)
        result = self.gateway.accept(headers, self.body, now=1010)
        self.assertEqual(result["status"], "duplicate")
        self.assertEqual(result["receipt"], first["receipt"])
        self.assertEqual(self.count("outbox"), 1)

    def test_revoked_key(self):
        gateway = Gateway(self.path, {"new": self.new})
        with self.assertRaises(Rejected) as result:
            gateway.accept(self.headers, self.body, now=1000)
        self.assertEqual(result.exception.status, 401)

    def test_same_event_with_different_content_conflicts(self):
        self.gateway.accept(self.headers, self.body, now=1000)
        body = b'{"type":"payment.settled","data":{"amount_cents":1}}'
        self.reject(409, headers=sign("old", self.old, "evt-1", body, 1000), body=body)
        self.assertEqual(self.count("outbox"), 1)

    def test_producers_have_separate_namespaces(self):
        other = SigningKey("shipping", b"s" * 32)
        gateway = Gateway(self.path, {"old": self.old, "shipping": other})
        gateway.accept(self.headers, self.body, now=1000)
        gateway.accept(sign("shipping", other, "evt-1", self.body, 1000), self.body, now=1000)
        self.assertEqual(self.count("outbox"), 2)

    def test_invalid_json_and_schema(self):
        for body in [b"[]", b'{"type":"x","data":{},"data":{}}', b'{"type":"x","data":{"n":NaN}}',
                     b'{"type":"x","data":[]}', b"\xff", b'{"type":"x","data":{},"extra":1}']:
            self.reject(400, headers=sign("old", self.old, "evt-1", body, 1000), body=body)
        self.assertEqual(self.count("outbox"), 0)

    def test_body_limit_and_malformed_headers(self):
        self.reject(413, body=b"x" * 65537)
        self.reject(400, headers={**self.headers, "timestamp": "01000"})
        self.reject(400, headers={**self.headers, "timestamp": 1000})
        self.reject(400, headers={**self.headers, "event_id": "bad\nevent"})
        self.reject(401, headers={**self.headers, "signature": "not-a-digest"})

    def test_concurrent_duplicate_delivery(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.gateway.accept(self.headers, self.body, now=1000), range(48)))
        self.assertEqual(sum(r["status"] == "accepted" for r in results), 1)
        self.assertEqual(len({r["receipt"] for r in results}), 1)
        self.assertEqual(self.count("outbox"), 1)

    def test_inbox_and_outbox_roll_back_together(self):
        with self.gateway.connect() as connection:
            connection.execute("CREATE TRIGGER reject_outbox BEFORE INSERT ON outbox BEGIN SELECT RAISE(ABORT,'test'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.gateway.accept(self.headers, self.body, now=1000)
        self.assertEqual(self.count("inbox"), 0)
        self.assertEqual(self.count("outbox"), 0)

    def test_worker_crash_and_stale_acknowledgement(self):
        self.gateway.accept(self.headers, self.body, now=1000)
        first = self.gateway.claim(now=1000, lease_seconds=10)
        self.assertIsNone(self.gateway.claim(now=1009))
        second = self.gateway.claim(now=1010)
        self.assertEqual(second["attempts"], 2)
        self.assertFalse(self.gateway.acknowledge(first["id"], first["token"]))
        self.assertTrue(self.gateway.acknowledge(second["id"], second["token"]))
        self.assertIsNone(self.gateway.claim(now=2000))

    def test_only_one_worker_claims_event(self):
        self.gateway.accept(self.headers, self.body, now=1000)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.gateway.claim(now=1000), range(16)))
        self.assertEqual(sum(result is not None for result in results), 1)

    def test_restart_retains_deduplication(self):
        self.gateway.accept(self.headers, self.body, now=1000)
        restarted = Gateway(self.path, {"old": self.old})
        self.assertEqual(restarted.accept(self.headers, self.body, now=1000)["status"], "duplicate")

    def test_short_keys_rejected(self):
        with self.assertRaises(ValueError):
            Gateway(self.path, {"bad": SigningKey("payments", b"short")})


if __name__ == "__main__":
    unittest.main()
