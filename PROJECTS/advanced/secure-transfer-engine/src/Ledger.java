package ledger;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

/** Single-writer, durable double-entry transfer core. Amounts are integer cents. */
public final class Ledger implements AutoCloseable {
    private static final int MAX_FRAME = 65_536;
    private final FileChannel journal;
    private final FileLock writerLock;
    private final Map<String, Account> accounts = new HashMap<>();
    private final Map<String, Transfer> transfers = new HashMap<>();
    private boolean closed;
    private boolean poisoned;

    public record Account(String id, String owner, long cents) {}
    public record Entry(String account, long delta) {}
    public record Receipt(String key, Entry debit, Entry credit) {}
    private record Transfer(String key, String actor, String from, String to, long cents) {
        Receipt receipt() {
            return new Receipt(key, new Entry(from, -cents), new Entry(to, cents));
        }
    }

    public static final class Rejected extends IllegalArgumentException {
        private static final long serialVersionUID = 1L;
        Rejected(String message) { super(message); }
    }

    public Ledger(Path path) throws IOException {
        journal = FileChannel.open(path, StandardOpenOption.CREATE,
                StandardOpenOption.READ, StandardOpenOption.WRITE);
        FileLock acquired = null;
        try {
            acquired = journal.tryLock();
            if (acquired == null) throw new IOException("Journal already has a writer");
            replay();
        } catch (IOException | RuntimeException failure) {
            if (acquired != null) acquired.release();
            journal.close();
            throw failure;
        }
        writerLock = acquired;
    }

    /** Administrative provisioning; call only from a trusted bootstrap path. */
    public synchronized void createAccount(String id, String owner, long cents) throws IOException {
        ready();
        identifier(id);
        identifier(owner);
        if (cents < 0 || accounts.containsKey(id)) throw new Rejected("Invalid account");
        byte[] record = encodeAccount(id, owner, cents);
        persist(record);
        accounts.put(id, new Account(id, owner, cents));
    }

    /** actor must come from an authenticated session, never the request body. */
    public synchronized Receipt transfer(String actor, String key, String from,
                                         String to, long cents) throws IOException {
        ready();
        Transfer request = new Transfer(key, actor, from, to, cents);
        authorize(request);
        Transfer existing = transfers.get(key);
        if (existing != null) {
            if (!existing.equals(request)) throw new Rejected("Idempotency key conflict");
            return existing.receipt();
        }
        validateFunds(request);
        persist(encodeTransfer(request));
        apply(request);
        return request.receipt();
    }

    public synchronized long balance(String actor, String id) throws IOException {
        ready();
        Account account = accounts.get(id);
        if (account == null || !account.owner().equals(actor)) throw new Rejected("Access denied");
        return account.cents();
    }

    /** Administrative snapshot; immutable and detached from subsequent transactions. */
    public synchronized Map<String, Account> snapshot() throws IOException {
        ready();
        return Map.copyOf(accounts);
    }

    private void authorize(Transfer request) {
        identifier(request.actor());
        identifier(request.key());
        identifier(request.from());
        identifier(request.to());
        Account source = accounts.get(request.from());
        if (source == null || !source.owner().equals(request.actor())) throw new Rejected("Access denied");
        if (request.from().equals(request.to()) || !accounts.containsKey(request.to()) || request.cents() <= 0)
            throw new Rejected("Invalid transfer");
    }

    private void validateFunds(Transfer request) {
        if (accounts.get(request.from()).cents() < request.cents()) throw new Rejected("Insufficient funds");
        try {
            Math.addExact(accounts.get(request.to()).cents(), request.cents());
        } catch (ArithmeticException overflow) {
            throw new Rejected("Destination balance overflow");
        }
    }

    private void apply(Transfer request) {
        Account source = accounts.get(request.from());
        Account destination = accounts.get(request.to());
        accounts.put(source.id(), new Account(source.id(), source.owner(), source.cents() - request.cents()));
        accounts.put(destination.id(), new Account(destination.id(), destination.owner(),
                Math.addExact(destination.cents(), request.cents())));
        transfers.put(request.key(), request);
    }

    private void ready() throws IOException {
        if (closed) throw new IOException("Ledger is closed");
        if (poisoned) throw new IOException("Journal write failed; close and inspect before reopening");
    }

    private static void identifier(String value) {
        if (value == null || !value.matches("[A-Za-z0-9_.:-]{1,128}")) throw new Rejected("Invalid identifier");
    }

    private void persist(byte[] record) throws IOException {
        ByteBuffer frame = ByteBuffer.allocate(4 + record.length + 32);
        frame.putInt(record.length).put(record).put(digest(record)).flip();
        try {
            journal.position(journal.size());
            while (frame.hasRemaining()) journal.write(frame);
            journal.force(true);
        } catch (IOException failure) {
            poisoned = true;
            throw failure;
        }
    }

    private void replay() throws IOException {
        journal.position(0);
        while (journal.position() < journal.size()) {
            ByteBuffer length = ByteBuffer.allocate(4);
            readFully(length);
            length.flip();
            int size = length.getInt();
            if (size <= 0 || size > MAX_FRAME) throw new IOException("Invalid journal frame size");
            ByteBuffer frame = ByteBuffer.allocate(size + 32);
            readFully(frame);
            byte[] record = Arrays.copyOfRange(frame.array(), 0, size);
            byte[] expected = Arrays.copyOfRange(frame.array(), size, size + 32);
            if (!MessageDigest.isEqual(digest(record), expected)) throw new IOException("Journal checksum mismatch");
            decode(record);
        }
    }

    private void readFully(ByteBuffer buffer) throws IOException {
        while (buffer.hasRemaining()) {
            if (journal.read(buffer) < 0) throw new EOFException("Incomplete journal frame; repair from a verified copy");
        }
    }

    private void decode(byte[] record) throws IOException {
        try (DataInputStream input = new DataInputStream(new ByteArrayInputStream(record))) {
            int version = input.readUnsignedByte();
            int type = input.readUnsignedByte();
            if (version != 1) throw new IOException("Unsupported journal version");
            if (type == 1) {
                String id = input.readUTF();
                String owner = input.readUTF();
                long cents = input.readLong();
                identifier(id);
                identifier(owner);
                if (cents < 0 || accounts.containsKey(id)) throw new IOException("Invalid account record");
                accounts.put(id, new Account(id, owner, cents));
            } else if (type == 2) {
                Transfer request = new Transfer(input.readUTF(), input.readUTF(), input.readUTF(),
                        input.readUTF(), input.readLong());
                authorize(request);
                validateFunds(request);
                if (transfers.containsKey(request.key())) throw new IOException("Duplicate journal key");
                apply(request);
            } else throw new IOException("Unknown journal record");
            if (input.available() != 0) throw new IOException("Trailing record bytes");
        } catch (IllegalArgumentException invalid) {
            throw new IOException("Journal violates ledger invariants", invalid);
        }
    }

    private static byte[] encodeAccount(String id, String owner, long cents) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (DataOutputStream output = new DataOutputStream(bytes)) {
            output.writeByte(1);
            output.writeByte(1);
            output.writeUTF(id);
            output.writeUTF(owner);
            output.writeLong(cents);
        }
        return bytes.toByteArray();
    }

    private static byte[] encodeTransfer(Transfer request) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (DataOutputStream output = new DataOutputStream(bytes)) {
            output.writeByte(1);
            output.writeByte(2);
            output.writeUTF(request.key());
            output.writeUTF(request.actor());
            output.writeUTF(request.from());
            output.writeUTF(request.to());
            output.writeLong(request.cents());
        }
        return bytes.toByteArray();
    }

    private static byte[] digest(byte[] bytes) {
        try { return MessageDigest.getInstance("SHA-256").digest(bytes); }
        catch (NoSuchAlgorithmException impossible) { throw new AssertionError(impossible); }
    }

    @Override
    public synchronized void close() throws IOException {
        if (!closed) {
            closed = true;
            try { writerLock.release(); }
            finally { journal.close(); }
        }
    }
}
