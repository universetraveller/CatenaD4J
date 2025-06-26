import org.apache.tools.ant.*;
import java.util.*;

public class NanoTimingListener implements BuildListener {

    private long taskStart;
    private Task currentTask;

    // Map task descriptions to elapsed nanoseconds
    private final Map<String, Long> timings = new HashMap<>();

    @Override
    public void taskStarted(BuildEvent event) {
        currentTask = event.getTask();
        taskStart = System.nanoTime();
    }

    @Override
    public void taskFinished(BuildEvent event) {
        long elapsedNs = System.nanoTime() - taskStart;

        Task task = event.getTask();
        String location = getLocationString(task);
        String key = String.format("%s at %s", task.getTaskName(), location);

        timings.merge(key, elapsedNs, Long::sum);

        System.out.printf("[PROFILE] Task %-15s took %8.3f ms (from %s)%n",
                task.getTaskName(),
                elapsedNs / 1_000_000.0,
                location);
    }

    @Override
    public void buildFinished(BuildEvent event) {
        System.out.println("\n=== Task timing ranking (slowest first) ===");
        timings.entrySet().stream()
            .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
            .forEach(e -> {
                double ms = e.getValue() / 1_000_000.0;
                System.out.printf("%8.3f ms : %s%n", ms, e.getKey());
            });
    }

    // Helper to get build file and line number if available
    private String getLocationString(Task task) {
        Location loc = task.getLocation();
        if (loc != null && loc.getFileName() != null) {
            return loc.getFileName() + ":" + loc.getLineNumber();
        }
        return "unknown location";
    }

    // Unused listener methods
    @Override public void buildStarted(BuildEvent event) {}
    @Override public void targetStarted(BuildEvent event) {}
    @Override public void targetFinished(BuildEvent event) {}
    @Override public void messageLogged(BuildEvent event) {}
}

