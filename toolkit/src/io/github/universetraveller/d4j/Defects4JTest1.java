package io.github.universetraveller.d4j;

import java.io.PrintStream;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.apache.tools.ant.taskdefs.optional.junit.FormatterElement;
import org.apache.tools.ant.taskdefs.optional.junit.JUnitTask;
import org.apache.tools.ant.taskdefs.optional.junit.JUnitTest;

import io.github.universetraveller.util.DevNullPrintStream;

import org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.SummaryAttribute;

/*
 * Runs tests from Defects4J projects using Ant's JUnitTask.
 */
public class Defects4JTest1 extends AbstractDefects4JTest {

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
        beforeGetClasspath();
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
}