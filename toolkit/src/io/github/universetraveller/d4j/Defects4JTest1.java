package io.github.universetraveller.d4j;

import java.io.IOException;
import java.io.PrintStream;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.tools.ant.taskdefs.optional.junit.FormatterElement;
import org.apache.tools.ant.taskdefs.optional.junit.JUnitTask;
import org.apache.tools.ant.taskdefs.optional.junit.JUnitTest;

import io.github.universetraveller.util.DevNullPrintStream;

import org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.SummaryAttribute;

/*
 * The target is to create a minimal test runner
 * some useful features like orderer, abort on failure, verify patches
 * that are not very important to a dataset are not added currently
 */
public class Defects4JTest1 extends Defects4JExport {

    Map<String, List<String>> methods;

    public Defects4JTest1(String projectBuildFile) throws MalformedURLException {
        super(projectBuildFile);

        methods = new HashMap<>();
    }

    public void run() throws Exception {
        String output = System.getProperty("OUTFILE");
        Path p = Paths.get(output).toAbsolutePath();
        Files.write(p, "".getBytes());
        output = System.getProperty("c4j.tests.printer.out");
        p = output == null ? p.getParent().resolve("all_tests") : Paths.get(output).toAbsolutePath();
        Files.write(p, "".getBytes());

        if(methods.isEmpty()) {
            // relevant tests are not handled by the super class
            // input them using args
            for(String clz : getTestsAll().split("\n")) {
                addTest(clz);
            }
        } 
        
        org.apache.tools.ant.types.Path path = new org.apache.tools.ant.types.Path(project);
        path.add((org.apache.tools.ant.types.Path) project.getReference("d4j.test.classpath"));

        JUnitTask junit = new JUnitTask();
        junit.setProject(project);
        SummaryAttribute sa = new SummaryAttribute();
        sa.setValue("yes");
        junit.setPrintsummary(sa);
        junit.setHaltonfailure(false);
        junit.setHaltonerror(false);
        junit.setFork(false);
        junit.setShowOutput(true);
        junit.createClasspath().add(path);;

        FormatterElement formatter = new FormatterElement();
        formatter.setClassname("io.github.universetraveller.util.AntJUnitFormatter");
        formatter.setUseFile(false);

        junit.addFormatter(formatter);

        JUnitTest test;
        List<JUnitTest> tests = new ArrayList<>();
        List<String> testMethods;
        for(String key : methods.keySet()) {
            test = new JUnitTest(key);
            testMethods = methods.get(key);
            if(testMethods != null) {
                test.setMethods(String.join(",", testMethods));
            }
            junit.addTest(test);
            tests.add(test);
        }

        PrintStream stdout = System.out;
        PrintStream stderr = System.err;
        PrintStream nullStream = new DevNullPrintStream();

        try{
            System.setOut(new PrintStream(nullStream));
            System.setErr(new PrintStream(nullStream));
            junit.execute();
        } finally {
            System.setOut(stdout);
            System.setErr(stderr);
        }

        output = System.getProperty("OUTFILE");
        p = Paths.get(output).toAbsolutePath();
        List<String> failingTests = new ArrayList<>();
        List<String> lines = Files.readAllLines(p);
        String line;
        for(int i = 0; i < lines.size(); ++i) {
            line = lines.get(i);
            if(line.trim().equals("---")) {
                i ++;
                failingTests.add(lines.get(i));
            }
        }

        System.out.println("Failing Tests: " + String.valueOf(failingTests.size()));
        for(String f : failingTests)
            System.out.println("    " + f);
    }

    public void addTest(String classOrTest) {
        int idx = classOrTest.indexOf('#');
        String className = idx < 0 ? classOrTest : classOrTest.substring(0, idx);
        methods.putIfAbsent(className, null);
        if(idx > 0) {
            if(methods.get(className) == null) {
                methods.put(className, new ArrayList<>());
            }
            methods.get(className).add(classOrTest.substring(idx + 1));
        }
    }

    public static void main(String[] args) throws IOException {
        Defects4JTest1 runner = new Defects4JTest1(args[0]);

        for(int i = 1; i < args.length; ++ i)
            runner.addTest(args[i]);
        
        try {
            runner.run();
            System.exit(0);
        } catch (Exception e) {
            throw new IOException(e);
        }
    }
}