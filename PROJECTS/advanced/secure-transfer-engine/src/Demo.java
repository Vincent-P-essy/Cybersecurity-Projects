package ledger;

import java.nio.file.*;

public final class Demo {
    private Demo() {}
    public static void main(String[] args) throws Exception {
        Path directory = Files.createTempDirectory("transfer-demo-");
        Path path = directory.resolve("ledger.bin");
        try {
            try (Ledger ledger = new Ledger(path)) {
                ledger.createAccount("alice-eur", "alice", 100_00);
                ledger.createAccount("bob-eur", "bob", 20_00);
                var receipt = ledger.transfer("alice", "payment-001", "alice-eur", "bob-eur", 15_00);
                ledger.transfer("alice", "payment-001", "alice-eur", "bob-eur", 15_00);
                System.out.println("Duplicate request: one debit, one credit");
                System.out.println(receipt);
                try { ledger.transfer("mallory", "payment-002", "alice-eur", "bob-eur", 1); }
                catch (Ledger.Rejected denied) { System.out.println("Cross-owner transfer: rejected"); }
            }
            try (Ledger ledger = new Ledger(path)) {
                System.out.printf("After restart: alice=%d cents, bob=%d cents%n",
                        ledger.balance("alice", "alice-eur"), ledger.balance("bob", "bob-eur"));
            }
        } finally {
            Files.deleteIfExists(path);
            Files.deleteIfExists(directory);
        }
    }
}
