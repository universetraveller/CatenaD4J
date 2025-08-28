package io.github.universetraveller.d4j;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.LinkedHashMap;
import java.util.Map;

import io.github.universetraveller.util.DevNullPrintStream;
import io.github.universetraveller.util.IsolatedClassLoader;

/*
 * The target is to create a minimal test runner
 * some useful features like orderer, abort on failure, verify patches
 * that are not very important to a dataset are not added currently
 */
public class Defects4JTest extends AbstractDefects4JTest {

    IsolatedClassLoader classLoader;

    public void initializeClassLoader(String[] pathElements) throws MalformedURLException {
        URL[] urls = new URL[pathElements.length + 1];

        for(int i = 0; i < pathElements.length; ++ i) {
            urls[i] = new File(pathElements[i]).toURI().toURL();
        }
        urls[pathElements.length] = getClass().getProtectionDomain().getCodeSource().getLocation();

        classLoader = new IsolatedClassLoader(urls, getClass().getClassLoader(), true, false);
        classLoader.addJREPackages();

        // using unified junit package as what ant's junit task does,
        // another approach is adding junit package to the beginning
        // of project's class path
        classLoader.addSystemPackageRoot("junit.");
        classLoader.addSystemPackageRoot("org.junit.");
        // in defects4j's ant version hamcrest should also be added
        // but in newer ant versions, junit related packages are loaded 
        // by SplitClassLoader so it is not required
        // junit 4 only depends on hamcrest and hamcrest doesn't depend on
        // other package, if it is not added, hamcrest will be loaded
        // by both System ClassLoader and IsolatedClassLoader which throws
        // an exception
        classLoader.addSystemPackageRoot("org.hamcrest.");

        // using null will skip all class loaders including the bootstrap class loader
        //classLoader = new URLClassLoader(urls, null);
    }

    public void initializeClassLoader1(String[] pathElements) throws MalformedURLException {
        // another implementation that also works
        URL[] urls = new URL[pathElements.length + 2];

        urls[0] = new File(project.getProperty("junit.jar")).toURI().toURL();

        int i = 1;
        for(String pathElement : pathElements) {
            urls[i++] = new File(pathElement).toURI().toURL(); 
        }

        urls[i] = getClass().getProtectionDomain().getCodeSource().getLocation();

        classLoader = new IsolatedClassLoader(urls, getClass().getClassLoader(), true, false);
        classLoader.addJREPackages();
    }

    public Defects4JTest(String projectBuildFile) throws MalformedURLException {
        super(projectBuildFile);

        // both LinkedHashMap and HashMap could cause some extra failing tests
        methods = new LinkedHashMap<>();

        String[] pathElements = getTestClasspath().split(":");

        initializeClassLoader(pathElements);
    }

    public void runTests() throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, IOException {
        Class<?> helper;
        Class<?> resultClass;

        // using JUnit4Helper here is ok, because all JUnitClassRunner classses have
        // implemented Filterable in junit version that defects4j's ant uses
        // the class OldTestClassRunner is deprecated so we do not need to handle it
        helper = classLoader.loadClass(System.getProperty("c4j.test.helper"));

        //try{
        //    resultClass = classLoader.loadClass("org.junit.runner.Result");
        //    helper = classLoader.loadClass("io.github.universetraveller.util.JUnit4Helper");
        //} catch (ClassNotFoundException e) {
        //    resultClass = classLoader.loadClass("junit.framework.TestResult");
        //    helper = classLoader.loadClass("io.github.universetraveller.util.JUnit3Helper");
        //}

        String listTests = System.getProperty("c4j.tests.printer.out");
        if(listTests != null) {
            Method builder = helper.getMethod("listTests", Map.class);
            Path path = Paths.get(listTests).toAbsolutePath();
            String tests = (String) builder.invoke(null, methods);
            Files.write(path, tests.getBytes());
            return;
        }

        // when using unified junit version
        resultClass = classLoader.loadClass("org.junit.runner.Result");

        PrintStream stdout = System.out;
        PrintStream stderr = System.err;
        PrintStream nullStream = new DevNullPrintStream();

        Method run = helper.getMethod("run", Map.class);
        Object result;

        try{
            System.setOut(new PrintStream(nullStream));
            System.setErr(new PrintStream(nullStream));
            result = run.invoke(null, methods);
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
            summary = (String) getFailingTests.invoke(null, result);
            Files.write(path, summary.getBytes());
        }
    }

    public void run() throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, IOException, Exception {
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

}