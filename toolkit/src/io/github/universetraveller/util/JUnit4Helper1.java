package io.github.universetraveller.util;

import java.io.IOException;
import java.net.URL;
import java.net.URLClassLoader;
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

/*
* A helper class to run each test class in a separate classloader.
*/
public class JUnit4Helper1 {
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

    public static String listTests(Map<String, List<String>> methods) throws ClassNotFoundException {
        List<String> result = new ArrayList<>();
        Request request = buildRequest(methods);
        collectDescriptions(request.getRunner().getDescription(), result);
        return String.join("\n", result);
    }

    public static Result run(Map<String, List<String>> methods) throws ClassNotFoundException {
        Set<String> keys = methods.keySet();

        Class<?> clazz;
        Filter ft;
        List<String> methodList;

        Result result = new Result();
        RunNotifier notifier = new RunNotifier();
        RunListener listener = result.createListener();
        Request request;
        Runner runner;
        notifier.addFirstListener(listener);

        ClassLoader parent = JUnit4Helper1.class.getClassLoader();
        URL[] urls = ((URLClassLoader) parent).getURLs();

        IsolatedClassLoader loader = new IsolatedClassLoader(urls, parent, true, false);
        loader.addJREPackages();
        loader.addSystemPackageRoot("junit.");
        loader.addSystemPackageRoot("org.junit.");
        loader.addSystemPackageRoot("org.hamcrest.");

        IsolatedClassLoader eachLoader;

        for(String key : keys) {
            eachLoader = loader.copy();
            Thread.currentThread().setContextClassLoader(eachLoader);
            clazz = eachLoader.loadClass(key);
            request = Request.aClass(clazz);

            methodList = methods.get(key);
            if(methodList != null) {
                ft = null;
                for(String method : methodList) {
                    ft = merge(ft, 
                            Filter.matchMethodDescription(
                                    Description.createTestDescription(clazz, method)
                                )                       
                            );
                }
                request = request.filterWith(ft);
            }

            runner =  request.getRunner();
            runner.run(notifier);
            Thread.currentThread().setContextClassLoader(parent);
        }
        notifier.removeListener(listener);
        try{
            loader.close();
        }catch(IOException e){}
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
        // should use general APIs for compatibility
        // if the junit version used by bugs is too low
        // it will raise java.lang.NoSuchMethodError for getClassName()Ljava/lang/String;
        // though we can use the getClassName version when using unified junit version
        // this version may be faster because the displayName is in a simple format
        String name = description.getDisplayName();
        int idx = name.indexOf('(');
        if (idx < 0) {
            return name;
        }
        return name.substring(idx + 1, name.length() - 1) + "#" + name.substring(0, idx);
    }

    public static String getFailingTestsSummary(Result result) {
        StringBuilder builder = new StringBuilder();

        List<Failure> failures = result.getFailures();

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
    
    public static String getFailingTests(Result result) {
        StringBuilder builder = new StringBuilder();

        String line;
        Throwable t;
        for (Failure f : result.getFailures()) {
            builder.append("---").append("\n");
            builder.append(formatDescription(f.getDescription())).append("\n");
            t = f.getException();
            builder.append(t.toString()).append("\n");
            for(StackTraceElement e : t.getStackTrace()) {
                line = e.toString();
                if(shouldRemoveTraceLine(line))
                    continue;
                builder.append("    " + line).append("\n");
            }
        }

        return builder.toString();
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
            request = request.filterWith(ft);
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
