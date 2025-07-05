package io.github.universetraveller.util;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.runner.Description;
import org.junit.runner.Request;
import org.junit.runner.Result;
import org.junit.runner.Runner;
import org.junit.runner.manipulation.Filter;
import org.junit.runner.notification.Failure;
import org.junit.runner.notification.RunListener;
import org.junit.runner.notification.RunNotifier;
//import org.junit.runner.notification.StoppedByUserException;

public class JUnit4Helper {
    final static String[] ignoredTraces = {
        "junit.",
        "org.junit.",
        "java.lang.reflect.Method.invoke(",
        "sun.reflect.",
        "io.github.universetraveller",
        //"org.apache.tools.ant.",
        //" more",
    };

    private static void collectDescriptions(Description description, List<String> result) {
        if (description.isTest()) {
            result.add(description.getDisplayName());
        } else {
            for (Description child : description.getChildren()) {
                collectDescriptions(child, result);
            }
        }
    }

    public static List<String> listTests(Map<String, List<String>> methods) throws ClassNotFoundException {
        List<String> result = new ArrayList<>();
        Request request = buildRequest(methods);
        collectDescriptions(request.getRunner().getDescription(), result);
        return result;
    }

    public static Result run(Map<String, List<String>> methods) throws ClassNotFoundException {
        Result result = new Result();
        RunNotifier notifier = new RunNotifier();
        Request request = buildRequest(methods);
        Runner runner =  request.getRunner();
        RunListener listener = result.createListener();
        notifier.addFirstListener(listener);
        try {
            notifier.fireTestRunStarted(runner.getDescription());
            runner.run(notifier);
            notifier.fireTestRunFinished(result);
        //} catch(StoppedByUserException e){
        //    notifier.fireTestRunFinished(result);
        } finally {
            notifier.removeListener(listener);
        }
        return result;
    }

    public static String getSummary(Result result) {
        return String.format("Run %s tests in %s ms; ignore %s tests; %s tests failed --- %s",
                             result.getRunCount(),
                             result.getRunTime(),
                             result.getIgnoreCount(),
                             result.getFailureCount(),
                             result.wasSuccessful() ? "PASS" : "FAIL");
    }

    public static String formatDescription(Description description) {
        return description.getClassName() + "#" + description.getMethodName();
    }

    public static String getFailingTestsSummary(Result result) {
        StringBuilder builder = new StringBuilder();

        List<Failure> failures = result.getFailures();

        Description desc;

        builder.append("Failing Tests: " + String.valueOf(failures.size()));
        for (Failure f : failures) {
            builder.append("\n");
            builder.append("    ");
            builder.append(formatDescription(f.getDescription()));
        }

        return builder.toString();
    }

    public static boolean shouldRemoveTraceLine(String line) {
        for(String p : ignoredTraces) {
            if(line.startsWith(p)) {
                return true;
            }
        }
        return false;
    }
    
    public static List<String> getFailingTests(Result result) {
        List<String> lines = new ArrayList<>();

        String line;
        Throwable t;
        for (Failure f : result.getFailures()) {
            lines.add("---");
            lines.add(formatDescription(f.getDescription()));
            t = f.getException();
            lines.add(t.toString());
            for(StackTraceElement e : t.getStackTrace()) {
                line = e.toString();
                if(shouldRemoveTraceLine(line))
                    continue;
                lines.add("    " + line);
            }
        }

        return lines;
    }

    public static Request buildRequest(Map<String, List<String>> methods) throws ClassNotFoundException {
        Set<String> keys = methods.keySet();

        Class<?>[] classes = new Class[keys.size()];
        Filter ft = null;

        Class<?> clazz;
        List<String> methodList;

        int idx = 0;
        for(String key : keys) {
            clazz = Class.forName(key);

            classes[idx++] = clazz;

            methodList = methods.get(key);
            if(methodList == null)
                continue;

            for(String method : methodList) {
                ft = merge(ft, 
                           Filter.matchMethodDescription(
                                   Description.createTestDescription(clazz, method)
                               )                       
                           );
            }
        }

        Request request = Request.classes(classes);

        if(ft != null) {
            request.filterWith(ft);
        }

        return request;
    }

    public static Filter merge(final Filter first, final Filter second) {
        if (second == first || first == null) {
            return second;
        }
        return new Filter() {
            @Override
            public boolean shouldRun(Description description) {
                return first.shouldRun(description)
                        || second.shouldRun(description);
            }

            @Override
            public String describe() {
                return first.describe() + " or " + second.describe();
            }
        };
    }
}
