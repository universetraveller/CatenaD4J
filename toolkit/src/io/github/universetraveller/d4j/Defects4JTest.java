package io.github.universetraveller.d4j;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.MalformedInputException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.universetraveller.util.DevNullPrintStream;

/*
 * The target is to create a minimal test runner
 * some useful features like orderer, abort on failure, verify patches
 * that are not very important to a dataset are not added currently
 */
public class Defects4JTest extends Defects4JExport {

    Map<String, List<String>> methods;
    URLClassLoader classLoader;
    boolean allAreClasses;

    public Defects4JTest(String projectBuildFile) throws MalformedURLException {
        super(projectBuildFile);

        methods = new HashMap<>();
        allAreClasses = true;

        String[] pathElements = getTestClasspath().split(":");
        URL[] urls = new URL[pathElements.length + 1];

        for(int i = 0; i < pathElements.length; ++ i) {
            urls[i] = new File(pathElements[i]).toURI().toURL();
        }
        urls[pathElements.length] = getClass().getProtectionDomain().getCodeSource().getLocation();

        classLoader = new URLClassLoader(urls, null);
    }

    public static void writeToFile(Path path, Iterable<? extends CharSequence> lines) throws IOException {
        try{
            Files.write(path, lines, StandardCharsets.UTF_8);
        } catch (MalformedInputException e) {
            Files.write(path, lines, StandardCharsets.ISO_8859_1);
        }
    }

    public void runTests() throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, IOException {
        Class<?> helper = classLoader.loadClass("io.github.universetraveller.util.JUnit4Helper");
        String listTests = System.getProperty("c4j.tests.printer.out");
        if(listTests != null) {
            Method builder = helper.getMethod("listTests", Map.class);
            Path path = Paths.get(listTests).toAbsolutePath();
            List<String> lines = new ArrayList<>();

            for(Object item : (List<?>) builder.invoke(null, methods))
                lines.add((String) item);

            writeToFile(path, lines);
            return;
        }

        Class<?> resultClass = classLoader.loadClass("org.junit.runner.Result");

        PrintStream stdout = System.out;
        PrintStream stderr = System.err;
        PrintStream nullStream = new DevNullPrintStream();

        Method builder = helper.getMethod("run", Map.class);
        Object result;

        try{
            System.setOut(new PrintStream(nullStream));
            System.setErr(new PrintStream(nullStream));
            result = builder.invoke(null, methods);
        } finally {
            System.setOut(stdout);
            System.setErr(stderr);
        }

        Method getSummary = helper.getMethod("getFailingTestsSummary", resultClass);
        String summary = (String) getSummary.invoke(null, result);
        System.out.println(summary);

        Method getFailingTests = helper.getMethod("getFailingTests", resultClass);
        String output = System.getProperty("OUTFILE");
        if(output != null) {
            Path path = Paths.get(output).toAbsolutePath();
            List<String> lines = new ArrayList<>();

            for(Object item : (List<?>) getFailingTests.invoke(null, result))
                lines.add((String) item);

            if(!lines.isEmpty())
                writeToFile(path, lines);
        }
    }

    public void run() throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, IOException {
        if(methods.isEmpty()) {
            // relevant tests are not handled by the super class
            // input them using args
            for(String clz : getTestsAll().split("\n")) {
                addTest(clz);
            }
        } 

        Thread t = Thread.currentThread();
        ClassLoader originalClassLoader = t.getContextClassLoader();
        try{
            t.setContextClassLoader(classLoader);
            runTests();
        } finally {
            t.setContextClassLoader(originalClassLoader);
        }
    }

    public void addTest(String classOrTest) {
        int idx = classOrTest.indexOf('#');
        String className = idx < 0 ? classOrTest : classOrTest.substring(0, idx);
        methods.putIfAbsent(className, null);
        if(idx > 0) {
            allAreClasses = false;
            if(methods.get(className) == null) {
                methods.put(className, new ArrayList<>());
            }
            methods.get(className).add(classOrTest.substring(idx + 1));
        }
    }

    public static void main(String[] args) throws IOException {
        Defects4JTest runner = new Defects4JTest(args[0]);

        for(int i = 1; i < args.length; ++ i)
            runner.addTest(args[i]);
        
        try {
            runner.run();
            System.exit(0);
        } catch (ClassNotFoundException | NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
            throw new IOException(e);
        }
    }
}