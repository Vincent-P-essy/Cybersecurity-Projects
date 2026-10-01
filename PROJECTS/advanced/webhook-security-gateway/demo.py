"""Exercise real admission, redelivery, and worker-crash recovery locally."""
import json
import secrets
import tempfile
from pathlib import Path

from gateway import Gateway, Rejected, SigningKey, sign


def main():
    key = SigningKey("payments", secrets.token_bytes(32))
    body = json.dumps({"type": "payment.settled", "data": {"invoice": "inv-42"}}).encode()
    with tempfile.TemporaryDirectory() as directory:
        gateway = Gateway(Path(directory) / "events.sqlite", {"current": key})
        headers = sign("current", key, "evt-42", body, 1000)
        print(gateway.accept(headers, body, now=1000)["status"])
        print(gateway.accept(headers, body, now=1000)["status"])
        try:
            gateway.accept(headers, body + b" ", now=1000)
        except Rejected as failure:
            print(f"Altered body: rejected ({failure.status})")
        first = gateway.claim(now=1000, lease_seconds=10)
        print("Worker claimed event, then stopped before acknowledgement")
        second = gateway.claim(now=1011)
        print(f"Recovered attempt: {second['attempts']}")
        print(f"Stale acknowledgement: {gateway.acknowledge(first['id'], first['token'])}")
        print(f"Current acknowledgement: {gateway.acknowledge(second['id'], second['token'])}")


if __name__ == "__main__":
    main()
