import org.apache.tools.ant.*;

public class NanoTimingListener implements BuildListener {
    private long taskStart;

    @Override
    public void taskStarted(BuildEvent event) {
        taskStart = System.nanoTime();
    }

    @Override
    public void taskFinished(BuildEvent event) {
        long elapsedNs = System.nanoTime() - taskStart;
        System.out.printf("[PROFILE] Task %s took %.3f ms%n", 
            event.getTask().getTaskName(), elapsedNs / 1_000_000.0);
    }

    @Override public void buildStarted(BuildEvent event) {}
    @Override public void buildFinished(BuildEvent event) {}
    @Override public void targetStarted(BuildEvent event) {}
    @Override public void targetFinished(BuildEvent event) {}
    @Override public void messageLogged(BuildEvent event) {}
}

