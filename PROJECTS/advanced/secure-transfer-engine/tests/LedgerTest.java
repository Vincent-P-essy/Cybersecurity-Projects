package ledger;

import java.io.IOException;
import java.nio.channels.OverlappingFileLockException;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public final class LedgerTest {
    private LedgerTest() {}
    private interface Scenario { void run(Path path) throws Exception; }
    private interface Action { void run() throws Exception; }
    private static int passed;

    private static void check(boolean condition) {
        if (!condition) throw new AssertionError("Invariant failed");
    }
    private static void rejects(Class<? extends Throwable> expected, Action action) throws Exception {
        try { action.run(); }
        catch (Throwable failure) {
            if (expected.isInstance(failure)) return;
            throw new AssertionError("Unexpected exception", failure);
        }
        throw new AssertionError("Expected " + expected.getSimpleName());
    }
    private static void scenario(String name, Scenario scenario) throws Exception {
        Path directory = Files.createTempDirectory("ledger-test-");
        Path path = directory.resolve("journal.bin");
        try {
            scenario.run(path);
            passed++;
            System.out.println("PASS " + name);
        } finally {
            Files.deleteIfExists(path);
            Files.deleteIfExists(directory);
        }
    }
    private static Ledger funded(Path path, long source) throws IOException {
        Ledger ledger = new Ledger(path);
        ledger.createAccount("a", "alice", source);
        ledger.createAccount("b", "bob", 0);
        return ledger;
    }
    private static void parallel(int count, Action action) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(8);
        try {
            List<Future<?>> futures = new ArrayList<>();
            for (int index = 0; index < count; index++) {
                futures.add(pool.submit(() -> {
                    try { action.run(); }
                    catch (Exception failure) { throw new RuntimeException(failure); }
                }));
            }
            for (Future<?> future : futures) future.get(20, TimeUnit.SECONDS);
        } finally {
            pool.shutdownNow();
        }
    }
    public static void main(String[] args) throws Exception {
        scenario("balanced entries", path -> {
            try (Ledger ledger = funded(path, 100)) {
                var receipt = ledger.transfer("alice", "one", "a", "b", 25);
                check(receipt.debit().delta() + receipt.credit().delta() == 0);
                check(ledger.balance("alice", "a") == 75 && ledger.balance("bob", "b") == 25);
            }
        });
        scenario("owner boundary", path -> {
            try (Ledger ledger = funded(path, 100)) {
                rejects(Ledger.Rejected.class, () -> ledger.transfer("bob", "one", "a", "b", 1));
                rejects(Ledger.Rejected.class, () -> ledger.balance("bob", "a"));
                check(ledger.balance("alice", "a") == 100);
            }
        });
        scenario("invalid amounts and identifiers", path -> {
            try (Ledger ledger = funded(path, 100)) {
                for (long amount : new long[]{0, -1, Long.MIN_VALUE, 101})
                    rejects(Ledger.Rejected.class, () -> ledger.transfer("alice", "one", "a", "b", amount));
                rejects(Ledger.Rejected.class, () -> ledger.transfer("alice", "../bad", "a", "b", 1));
                rejects(Ledger.Rejected.class, () -> ledger.transfer("alice", "one", "a", "a", 1));
                rejects(Ledger.Rejected.class, () -> ledger.transfer("alice", "one", "a", "missing", 1));
                rejects(Ledger.Rejected.class, () -> ledger.createAccount("a", "alice", 1));
            }
        });
        scenario("idempotency and conflict", path -> {
            try (Ledger ledger = funded(path, 100)) {
                var receipt = ledger.transfer("alice", "same", "a", "b", 100);
                check(receipt.equals(ledger.transfer("alice", "same", "a", "b", 100)));
                rejects(Ledger.Rejected.class, () -> ledger.transfer("alice", "same", "a", "b", 99));
                check(ledger.balance("bob", "b") == 100);
            }
        });
        scenario("overflow is atomic", path -> {
            try (Ledger ledger = funded(path, 100)) {
                ledger.createAccount("full", "bob", Long.MAX_VALUE);
                rejects(Ledger.Rejected.class, () -> ledger.transfer("alice", "overflow", "a", "full", 1));
                check(ledger.balance("alice", "a") == 100);
            }
        });
        scenario("replay retains balances and idempotency", path -> {
            try (Ledger ledger = funded(path, 100)) { ledger.transfer("alice", "same", "a", "b", 40); }
            try (Ledger ledger = new Ledger(path)) {
                ledger.transfer("alice", "same", "a", "b", 40);
                check(ledger.balance("alice", "a") == 60 && ledger.balance("bob", "b") == 40);
            }
        });
        scenario("concurrent duplicate delivery", path -> {
            try (Ledger ledger = funded(path, 100)) {
                parallel(64, () -> ledger.transfer("alice", "duplicate", "a", "b", 10));
                check(ledger.balance("alice", "a") == 90 && ledger.balance("bob", "b") == 10);
            }
        });
        scenario("concurrent overdraft prevention", path -> {
            try (Ledger ledger = funded(path, 100)) {
                AtomicInteger keys = new AtomicInteger();
                AtomicInteger accepted = new AtomicInteger();
                parallel(64, () -> {
                    try { ledger.transfer("alice", "k" + keys.incrementAndGet(), "a", "b", 10); accepted.incrementAndGet(); }
                    catch (Ledger.Rejected insufficient) { check(insufficient.getMessage().equals("Insufficient funds")); }
                });
                check(accepted.get() == 10 && ledger.balance("alice", "a") == 0 && ledger.balance("bob", "b") == 100);
            }
        });
        scenario("randomized conservation", path -> {
            try (Ledger ledger = funded(path, 10000)) {
                Random random = new Random(41);
                for (int index = 0; index < 250; index++) {
                    boolean forward = random.nextBoolean();
                    String from = forward ? "a" : "b", to = forward ? "b" : "a";
                    String actor = forward ? "alice" : "bob";
                    long amount = random.nextInt(200) + 1;
                    if (ledger.balance(actor, from) >= amount) ledger.transfer(actor, "r" + index, from, to, amount);
                    check(ledger.balance("alice", "a") + ledger.balance("bob", "b") == 10000);
                }
            }
        });
        scenario("single writer", path -> {
            try (Ledger ledger = funded(path, 100)) {
                check(ledger.balance("alice", "a") == 100);
                rejects(OverlappingFileLockException.class, () -> {
                    try (Ledger competing = new Ledger(path)) { competing.snapshot(); }
                });
            }
        });
        scenario("checksum corruption rejected", path -> {
            try (Ledger ledger = funded(path, 100)) { ledger.snapshot(); }
            byte[] bytes = Files.readAllBytes(path);
            bytes[12] ^= 1;
            Files.write(path, bytes);
            rejects(IOException.class, () -> { try (Ledger ledger = new Ledger(path)) { ledger.snapshot(); } });
        });
        scenario("torn frame rejected", path -> {
            try (Ledger ledger = funded(path, 100)) { ledger.snapshot(); }
            byte[] bytes = Files.readAllBytes(path);
            Files.write(path, Arrays.copyOf(bytes, bytes.length - 1));
            rejects(IOException.class, () -> { try (Ledger ledger = new Ledger(path)) { ledger.snapshot(); } });
        });
        scenario("oversized frame rejected", path -> {
            Files.write(path, new byte[]{127, -1, -1, -1});
            rejects(IOException.class, () -> { try (Ledger ledger = new Ledger(path)) { ledger.snapshot(); } });
        });
        scenario("closed instance rejects operations", path -> {
            Ledger ledger = funded(path, 100);
            ledger.close();
            rejects(IOException.class, () -> ledger.transfer("alice", "one", "a", "b", 1));
            ledger.close();
        });
        System.out.println(passed + " scenarios passed");
    }
}
