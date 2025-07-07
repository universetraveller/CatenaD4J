package io.github.universetraveller.junit.agent;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

public class JUnitRecorder {
    public static class FailureRecord {
        public final String message;
        public final List<String> userStack;

        public FailureRecord(String message, List<String> userStack) {
            this.message = message;
            this.userStack = userStack;
        }
    }

    private static final Queue<FailureRecord> records = new ConcurrentLinkedQueue<>();

    public static void record(String message, List<String> userStack) {
        records.add(new FailureRecord(message, userStack));
    }

    public static List<FailureRecord> getFailures() {
        return new ArrayList<>(records); // fast copy at the end
    }

    public static void clear() {
        records.clear();
    }
}


