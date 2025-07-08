package io.github.universetraveller.util;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

import org.apache.tools.ant.taskdefs.optional.junit.JUnitResultFormatter;
import org.apache.tools.ant.taskdefs.optional.junit.JUnitTest;

import junit.framework.AssertionFailedError;
import junit.framework.Test;
import junit.framework.TestCase;

public class AntJUnitFormatter implements JUnitResultFormatter {
    final static String[] ignoredTraces = {
        "junit.",
        "org.junit.",
        "java.lang.reflect.Method.invoke(",
        "sun.reflect.",
        "io.github.universetraveller",
        "org.apache.tools.ant.",
        //" more",
    };

    public static boolean shouldRemoveTraceLine(String line) {
        for(String p : ignoredTraces) {
            if(line.startsWith(p)) {
                return true;
            }
        }
        return false;
    }

    public static String formatTest(Test test) {
        if(test instanceof TestCase) {
            TestCase testCase = (TestCase) test;
            return testCase.getClass().getName() + "#" + testCase.getName();
        }
        return test.toString();
    }

    StringBuilder failedTests = new StringBuilder();
    StringBuilder allTests = new StringBuilder();

    @Override
    public void addFailure(Test test, AssertionFailedError error) {
        this.addError(test, error);
    }

    @Override
    public void addError(Test test, Throwable error) {
        String line;
        failedTests.append("---").append("\n");
        failedTests.append(formatTest(test)).append("\n");
        failedTests.append(error.toString()).append("\n");
        for(StackTraceElement element : error.getStackTrace()) {
            line = element.toString();
            if(shouldRemoveTraceLine(line))
                continue;
            failedTests.append("    " + line).append("\n");
        }
    }

    // Implement other required methods (no-ops if not needed)
    @Override public void startTestSuite(JUnitTest suite) {}
    @Override
    public void endTestSuite(JUnitTest suite) {
        try{
            String output = System.getProperty("OUTFILE");
            Path path = Paths.get(output).toAbsolutePath();
            Files.write(path, failedTests.toString().getBytes(), StandardOpenOption.APPEND);
            output = System.getProperty("c4j.tests.printer.out");
            path = output == null ? path.getParent().resolve("all_tests") : Paths.get(output).toAbsolutePath();
            Files.write(path, allTests.toString().getBytes(), StandardOpenOption.APPEND);
        }catch(IOException e) {
            throw new RuntimeException(e);
        }
    }
    @Override
    public void startTest(Test test) {
        allTests.append(test.toString()).append("\n");
    }
    @Override public void endTest(Test test) {}
    @Override public void setOutput(OutputStream out) {}
    @Override public void setSystemOutput(String out) {}
    @Override public void setSystemError(String err) {}
}
