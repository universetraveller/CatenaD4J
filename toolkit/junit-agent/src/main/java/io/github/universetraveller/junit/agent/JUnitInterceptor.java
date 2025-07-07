package io.github.universetraveller.junit.agent;

import java.util.ArrayList;
import java.util.List;

public class JUnitInterceptor {
    final static String[] EXCLUDED_PACKAGES = {
        "junit.",
        "org.junit.",
        "java.lang.reflect.Method.invoke(",
        "sun.reflect.",
        "io.github.universetraveller",
        //"org.gradle.",
        //"org.apache.maven.",
        //"org.apache.tools.ant.",
    };

    public static void intercept(String message) {
        StackTraceElement[] stack = new Exception().getStackTrace(); // skips interceptor itself

        List<String> userFrames = new ArrayList<>();
        for (int i = 1; i < stack.length; i++) {
            StackTraceElement frame = stack[i];
            String className = frame.getClassName();

            if (!isExcluded(className)) {
                userFrames.add(frame.toString());
            }
        }

        JUnitRecorder.record(message, userFrames);
    }

    private static boolean isExcluded(String className) {
        for (String prefix : EXCLUDED_PACKAGES) {
            if (className.startsWith(prefix)) return true;
        }
        return false;
    }
}
