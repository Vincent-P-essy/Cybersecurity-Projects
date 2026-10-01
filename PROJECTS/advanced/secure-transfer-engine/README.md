# Secure Transfer Engine

A Java 17 transfer core that keeps the important promises small and testable:
every accepted transfer has a matching debit and credit, retries do not debit
twice, concurrent requests cannot overdraw an account, and a restart retains
both balances and idempotency keys.

## Run

Requires a Java 17+ runtime with the `jdk.compiler` module. No Maven, framework,
database server, network access, or third-party dependency is needed.

```bash
bash run.sh test
bash run.sh demo
```

The demo transfers 1,500 cents, repeats the same request, rejects a different
account owner, then reopens the journal. Final balances are 8,500 and 3,500
cents. It uses a temporary directory and removes its fixture afterwards.

## Design

| Property | Mechanism |
|---|---|
| Balanced postings | A receipt contains one negative and one positive entry of equal magnitude |
| Exact amounts | Signed `long` integer cents; positive amounts and destination overflow checked before writing |
| Ownership boundary | Source owner must match the supplied authenticated principal |
| Idempotency | Key is bound to principal, source, destination and amount; a changed request conflicts |
| Concurrency | Transfers are serialized within one instance; a file lock admits one journal writer |
| Restart recovery | Versioned binary records replay into balances and the idempotency index |
| Persistence ordering | Complete frame and SHA-256 checksum are forced to disk before memory changes |
| Corruption handling | Invalid checksums, oversized records and incomplete frames fail closed |

```java
try (Ledger ledger = new Ledger(Path.of("ledger.bin"))) {
    // Trusted provisioning path, separate from customer requests.
    ledger.createAccount("alice-eur", "alice", 100_00);
    ledger.createAccount("bob-eur", "bob", 20_00);
    ledger.transfer("alice", "payment-001", "alice-eur", "bob-eur", 15_00);
}
```

`actor` belongs to the authentication adapter. A future HTTP adapter must derive
it from a verified session rather than copy it from client JSON. Account creation
and administrative snapshots are trusted operations and must not be exposed to
customers. This module implements domain authorization, not login or token verification.

## Validation

Fourteen test scenarios cover owner isolation, invalid requests, duplicate and
conflicting keys, numeric overflow, restart recovery, single-writer enforcement,
concurrent duplicate delivery, concurrent overdraft prevention, corrupted and
torn journals, and operations after close. A seeded randomized test checks total
balance conservation after every accepted transfer.

Compilation uses `-Xlint:all -Werror`. Tests run without assertions being disabled
by JVM flags: failed conditions throw directly and exit with a nonzero status.

## Operating limits

- One currency per ledger; no exchange rates, interest, fees, or settlement network.
- One local writer and a trusted private journal directory. Apply restrictive file
  permissions such as `umask 077`; this is not a distributed database.
- The checksum detects accidental corruption, not an attacker who can rewrite
  records and recompute hashes. Protect journal storage and retain verified backups.
- A failed disk write poisons the live instance. A partial final frame is rejected
  on reopen and requires recovery from a verified copy; no automatic truncation.
- Durability depends on filesystem and device guarantees. Journal compaction,
  database replication, transport authentication and operational monitoring remain
  separate integration work. This is a reference core, not a banking production system.
