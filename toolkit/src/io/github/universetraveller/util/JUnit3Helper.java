package io.github.universetraveller.util;

import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.Map;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestFailure;
import junit.framework.TestResult;
import junit.framework.TestSuite;

/*
 * Some projects' class path contains no junit 4 so we should have a junit 3
 * version for compatibility to run tests without inserting new entry to class path
 */
public class JUnit3Helper {
    final static String[] ignoredTraces = {
        "junit.",
        "org.junit.",
        "java.lang.reflect.Method.invoke(",
        "sun.reflect.",
        "io.github.universetraveller",
        //"org.apache.tools.ant.",
        //" more",
    };

    public static String formatTest(Test test) {
        if(test instanceof TestCase) {
            TestCase testCase = (TestCase) test;
            return testCase.getClass().getName() + "#" + testCase.getName();
        }
        return test.toString();
    }

    public static void listTestMethods(Test test, List<String> result) {
        if (test instanceof TestSuite) {
            TestSuite suite = (TestSuite) test;
            for (int i = 0; i < suite.testCount(); i++) {
                Test child = suite.testAt(i);
                listTestMethods(child, result);
            }
        } else if (test instanceof TestCase) {
            TestCase testCase = (TestCase) test;
            result.add(testCase.getName() + "(" + testCase.getClass().getName() + ")");
        }
    }

    public static List<String> listTests(Map<String, List<String>> methods) throws ClassNotFoundException {
        List<String> result = new ArrayList<>();
        TestSuite suite = buildTestSuite(methods);
        listTestMethods(suite, result);
        return result;
    }

    public static TestResult run(Map<String, List<String>> methods) throws ClassNotFoundException {
        TestSuite suite = buildTestSuite(methods);
        TestResult result = new TestResult();
        suite.run(result);
        return result;
    }

    public static String getFailingTestsSummary(TestResult result) {
        StringBuilder builder = new StringBuilder();

        builder.append("Failing Tests: " + String.valueOf(result.failureCount() + result.errorCount()));

        Enumeration<TestFailure> e = result.failures();
        boolean readErrors = false;
        TestFailure f;

        while(true) {
            if(!e.hasMoreElements()) {
                if (readErrors) break;
                e = result.errors();
                readErrors = true;
                continue;
            }
            f = (TestFailure) e.nextElement();
            builder.append("\n");
            builder.append("    ");
            builder.append(formatTest(f.failedTest()));
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

    public static List<String> getFailingTests(TestResult result) {
        List<String> lines = new ArrayList<>();

        String line;
        Throwable t;

        Enumeration<TestFailure> e = result.failures();
        boolean readErrors = false;
        TestFailure f;

        while(true) {
            if(!e.hasMoreElements()) {
                if (readErrors) break;
                e = result.errors();
                readErrors = true;
                continue;
            }
            f = (TestFailure) e.nextElement();
            lines.add("---");
            lines.add(formatTest(f.failedTest()));
            t = f.thrownException();
            lines.add(t.toString());
            for(StackTraceElement element : t.getStackTrace()) {
                line = element.toString();
                if(shouldRemoveTraceLine(line))
                    continue;
                lines.add("    " + line);
            }
        }

        return lines;
    }

    public static TestSuite buildTestSuite(Map<String, List<String>> methods) throws ClassNotFoundException {
        TestSuite suite = new TestSuite();

        Class<?> clazz;
        List<String> methodList;

        for(String key : methods.keySet()) {
            clazz = Class.forName(key);

            methodList = methods.get(key);
            if(methodList == null) {
                // run the whole class
                suite.addTest(new TestSuite(clazz));
                continue;
            }

            // run specified methods
            for(String method : methodList) {
                suite.addTest(TestSuite.createTest(clazz, method));
            }

        }

        return suite;
    }
}
