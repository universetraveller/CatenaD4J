# CatenaD4J Java Toolkit API Documentation

This document provides detailed API documentation for the Java toolkit component of CatenaD4J, which includes test execution utilities, Ant tasks, and Defects4J integration classes.

## Table of Contents

- [Overview](#overview)
- [Defects4J Integration](#defects4j-integration)
- [JUnit Agent](#junit-agent)
- [Test Execution Utilities](#test-execution-utilities)
- [Ant Custom Tasks](#ant-custom-tasks)
- [Utility Classes](#utility-classes)
- [Examples](#examples)

## Overview

The Java toolkit is located in the `toolkit/` directory and provides:

- **Defects4J Integration**: Classes for exporting properties and executing tests
- **JUnit Agent**: Bytecode instrumentation for intercepting test failures
- **Test Runners**: JUnit 3 and JUnit 4 test execution helpers
- **Ant Tasks**: Custom Ant tasks for build automation
- **Utilities**: ClassLoader isolation, class discovery, and formatting

## Defects4J Integration

Package: `io.github.universetraveller.d4j`

These classes provide integration with Defects4J and property export functionality.

### Class: `Defects4JExport`

Exports static and dynamic properties for Defects4J bugs.

**Package:** `io.github.universetraveller.d4j`

**Purpose:** Export version-specific properties like classpaths, test lists, and directory paths.

**Constructors:**

```java
public Defects4JExport(String projectBuildFile)
```
Initialize with a project build file path.

**Parameters:**
- `projectBuildFile`: Path to the Ant build.xml file

**System Properties Required:**
- `c4j.d4j.properties`: Path to Defects4J properties file
- `basedir`: Base directory of the project

**Static Properties:**
- `classes.modified`: Classes modified by the bug fix
- `classes.relevant`: Classes loaded by triggering tests
- `dir.src.classes`: Source directory of classes
- `dir.src.tests`: Source directory of tests
- `tests.trigger`: Trigger tests that expose the bug
- `tests.relevant`: Relevant tests touching modified sources

**Dynamic Properties:**
- `cp.compile`: Classpath to compile the project
- `cp.test`: Classpath to compile and run tests
- `dir.bin.classes`: Target directory of classes
- `dir.bin.tests`: Target directory of test classes
- `tests.all`: List of all developer-written tests

**Example:**
```java
// Set required system properties
System.setProperty("c4j.d4j.properties", "/path/to/defects4j.properties");
System.setProperty("basedir", "/path/to/project");

// Create exporter
Defects4JExport exporter = new Defects4JExport("/path/to/build.xml");

// Export is typically invoked via Ant tasks
```

### Class: `Defects4JStartup`

Base class for Defects4J integration providing initialization and common functionality.

**Package:** `io.github.universetraveller.d4j`

**Extends:** Ant Project

**Purpose:** Initialize project infrastructure and manage Ant build environment.

**Protected Methods:**

```java
protected void initializeDefects4J(String propertiesFile, String baseDir)
```
Initialize Defects4J properties and environment.

```java
protected void initializeProjectHelper2()
```
Initialize Ant ProjectHelper for build file processing.

### Class: `Defects4JTest`

Minimal test runner for executing JUnit tests in isolation.

**Package:** `io.github.universetraveller.d4j`

**Purpose:** Execute developer-written tests with isolated classloaders to avoid interference.

**Methods:**

```java
public void initializeClassLoader(String[] pathElements) throws MalformedURLException
```
Initialize an isolated classloader with specified classpath.

**Parameters:**
- `pathElements`: Array of classpath entries

**Features:**
- Isolated classloader prevents class conflicts
- Supports both JUnit 3 and JUnit 4
- Minimal overhead compared to Ant junit task
- Abort-on-failure capability (in subclasses)

**Example:**
```java
Defects4JTest testRunner = new Defects4JTest();

// Initialize with classpath
String[] classpath = {
    "/path/to/classes",
    "/path/to/test-classes",
    "/path/to/junit.jar"
};
testRunner.initializeClassLoader(classpath);

// Execution details in subclass implementations
```

### Class: `AbstractDefects4JTest`

Abstract base for test execution with common functionality.

**Package:** `io.github.universetraveller.d4j`

**Purpose:** Provide common test execution infrastructure.

**Abstract:** Yes

### Class: `Defects4JExecute`

Main entry point for executing Defects4J-related operations.

**Package:** `io.github.universetraveller.d4j`

**Purpose:** Execute export or test operations from command line.

**Main Method:**
```java
public static void main(String[] args)
```

## JUnit Agent

Package: `io.github.universetraveller.junit.agent`

A Java agent for instrumenting JUnit test execution to intercept and record test failures.

### Class: `JUnitAgent`

Java agent that instruments JUnit Assert.fail() calls.

**Package:** `io.github.universetraveller.junit.agent`

**Purpose:** Intercept JUnit assertions to track failure locations and messages.

**Agent Entry Point:**

```java
public static void premain(String agentArgs, Instrumentation inst)
```
Entry point called by JVM when agent is loaded.

**Usage:**
```bash
java -javaagent:/path/to/junit-agent.jar -jar your-tests.jar
```

**Features:**
- Intercepts `Assert.fail(String)` calls
- Records failure messages and stack traces
- Prints detailed failure information on shutdown
- No modification to test code required

**Output Format:**
```
=== Intercepted Assert.fail(String) Calls ===
fail("Expected exception not thrown")
Caused by:
  com.example.MyTest.testException(MyTest.java:42)
  ...
---
=== Length: 1 ===
```

### Class: `JUnitRecorder`

Records test failure information captured by the agent.

**Package:** `io.github.universetraveller.junit.agent`

**Purpose:** Thread-safe storage for failure records.

**Inner Class:**

```java
public static class FailureRecord {
    public final String message;
    public final List<String> userStack;
}
```

**Methods:**

```java
public static void record(String message, List<String> userStack)
```
Record a test failure with message and stack trace.

```java
public static List<FailureRecord> getFailures()
```
Get all recorded failures.

**Returns:** List of FailureRecord objects

```java
public static void clear()
```
Clear all recorded failures.

### Class: `JUnitTransformer`

Bytecode transformer for instrumenting JUnit classes.

**Package:** `io.github.universetraveller.junit.agent`

**Purpose:** Transform Assert.fail() calls to record failures.

**Installation:**
```java
public static void install(Instrumentation inst)
```
Install the transformer into the JVM.

### Class: `JUnitInterceptor`

Interceptor methods called from instrumented code.

**Package:** `io.github.universetraveller.junit.agent`

**Purpose:** Provide interception points for transformed bytecode.

## Test Execution Utilities

Package: `io.github.universetraveller.util`

Utilities for executing JUnit 3 and JUnit 4 tests.

### Class: `JUnit4Helper`

Helper for executing JUnit 4 tests programmatically.

**Package:** `io.github.universetraveller.util`

**Purpose:** Execute JUnit 4 tests and format results.

**Static Methods:**

```java
public static String listTests(Map<String, List<String>> methods) 
    throws ClassNotFoundException
```
List all test methods in the specified classes.

**Parameters:**
- `methods`: Map of class names to method name lists

**Returns:** Newline-separated list of test names

```java
public static Result run(Map<String, List<String>> methods) 
    throws ClassNotFoundException
```
Execute the specified test methods.

**Parameters:**
- `methods`: Map of class names to method name lists

**Returns:** JUnit Result object

```java
public static String getSummary(Result result)
```
Generate a summary string for test results.

**Returns:** Summary in format: "Run X tests in Y ms; ignore Z tests; W tests failed --- PASS/FAIL"

```java
public static String getFailingTestsSummary(Result result)
```
Generate summary of failing tests.

**Returns:** List of failed test names with descriptions

```java
public static String formatDescription(Description description)
```
Format a test description in standard format.

**Returns:** String in format "ClassName#methodName"

**Example:**
```java
import io.github.universetraveller.util.JUnit4Helper;
import org.junit.runner.Result;
import java.util.*;

// Define tests to run
Map<String, List<String>> tests = new HashMap<>();
tests.put("com.example.MyTest", Arrays.asList("testMethod1", "testMethod2"));
tests.put("com.example.OtherTest", Arrays.asList("testMethod3"));

// Execute tests
Result result = JUnit4Helper.run(tests);

// Print summary
System.out.println(JUnit4Helper.getSummary(result));

// Print failures if any
if (!result.wasSuccessful()) {
    System.out.println(JUnit4Helper.getFailingTestsSummary(result));
}
```

### Class: `JUnit4Helper1`

Extended JUnit 4 helper with additional formatting options.

**Package:** `io.github.universetraveller.util`

**Purpose:** Alternative implementation with different formatting.

**Methods:** Similar to JUnit4Helper with implementation variations

### Class: `JUnit3Helper`

Helper for executing JUnit 3 tests programmatically.

**Package:** `io.github.universetraveller.util`

**Purpose:** Execute JUnit 3 TestCase-based tests.

**Static Methods:**

```java
public static String listTests(Map<String, List<String>> methods) 
    throws ClassNotFoundException
```
List all JUnit 3 test methods.

```java
public static TestResult run(Map<String, List<String>> methods) 
    throws ClassNotFoundException
```
Execute JUnit 3 tests.

**Returns:** junit.framework.TestResult object

```java
public static String getSummary(TestResult result)
```
Generate summary for JUnit 3 test results.

```java
public static String getFailingTestsSummary(TestResult result)
```
Generate summary of failing JUnit 3 tests.

**Example:**
```java
import io.github.universetraveller.util.JUnit3Helper;
import junit.framework.TestResult;
import java.util.*;

Map<String, List<String>> tests = new HashMap<>();
tests.put("com.example.LegacyTest", Arrays.asList("testOldStyle"));

TestResult result = JUnit3Helper.run(tests);
System.out.println(JUnit3Helper.getSummary(result));
```

## Ant Custom Tasks

Package: `io.github.universetraveller.ant`

Custom Ant tasks for build automation.

### Class: `AppendProperty`

Ant task to append a value to an existing property.

**Package:** `io.github.universetraveller.ant`

**Extends:** org.apache.tools.ant.Task

**Purpose:** Append to properties with a separator (useful for classpaths).

**Attributes:**
- `propertyName`: Name of the property to modify
- `value`: Value to append
- `sep`: Separator (default: ":")

**Build File Usage:**
```xml
<taskdef name="appendProperty" 
         classname="io.github.universetraveller.ant.AppendProperty"/>

<property name="classpath" value="/path/to/lib1.jar"/>
<appendProperty propertyName="classpath" 
                value="/path/to/lib2.jar" 
                sep=":"/>
<!-- classpath now contains "/path/to/lib1.jar:/path/to/lib2.jar" -->
```

### Class: `CheckTargetExists`

Ant task to check if a target exists in the build file.

**Package:** `io.github.universetraveller.ant`

**Purpose:** Conditionally execute based on target existence.

**Attributes:**
- `target`: Target name to check
- `property`: Property to set if target exists

**Build File Usage:**
```xml
<taskdef name="checkTarget" 
         classname="io.github.universetraveller.ant.CheckTargetExists"/>

<checkTarget target="compile.tests" property="has.test.target"/>

<target name="conditional" if="has.test.target">
    <antcall target="compile.tests"/>
</target>
```

### Class: `DynamicNoOpTask`

Ant task that accepts any attributes but does nothing.

**Package:** `io.github.universetraveller.ant`

**Purpose:** Stub out tasks during testing or selective execution.

**Build File Usage:**
```xml
<taskdef name="noop" 
         classname="io.github.universetraveller.ant.DynamicNoOpTask"/>

<!-- Accepts any attributes, does nothing -->
<noop anything="value" whatever="data"/>
```

### Class: `CheckAndRename`

Ant task for conditional file operations.

**Package:** `io.github.universetraveller.ant`

**Purpose:** Check file existence and perform rename operations.

### Class: `FilterPath`

Ant task to filter path elements based on existence or patterns.

**Package:** `io.github.universetraveller.ant`

**Purpose:** Clean up classpaths by removing non-existent entries.

**Build File Usage:**
```xml
<taskdef name="filterPath" 
         classname="io.github.universetraveller.ant.FilterPath"/>

<filterPath pathId="project.classpath" 
            outputProperty="filtered.classpath"
            existsOnly="true"/>
```

## Utility Classes

Package: `io.github.universetraveller.util`

### Class: `IsolatedClassLoader`

ClassLoader that isolates loaded classes from parent classloader.

**Package:** `io.github.universetraveller.util`

**Extends:** URLClassLoader

**Purpose:** Prevent class conflicts by loading classes in isolation.

**Constructor:**

```java
public IsolatedClassLoader(URL[] urls, ClassLoader parent, 
                          boolean parentFirst, boolean isolated)
```

**Parameters:**
- `urls`: Classpath URLs
- `parent`: Parent classloader
- `parentFirst`: Whether to delegate to parent first
- `isolated`: Whether to fully isolate from parent

**Methods:**

```java
public void addJREPackages()
```
Add JRE packages to system packages list.

```java
public void addSystemPackageRoot(String packageRoot)
```
Add a package prefix to load from system classloader.

**Example:**
```java
URL[] urls = {new File("/path/to/classes").toURI().toURL()};
IsolatedClassLoader loader = new IsolatedClassLoader(
    urls, 
    getClass().getClassLoader(), 
    true, 
    false
);

// Load JUnit from system classloader
loader.addSystemPackageRoot("org.junit.");

// Load test class in isolation
Class<?> testClass = loader.loadClass("com.example.MyTest");
```

### Class: `ControlledURLClassLoader`

URLClassLoader with fine-grained control over class loading.

**Package:** `io.github.universetraveller.util`

**Purpose:** Advanced classloader with explicit control over delegation.

**Methods:** Similar to IsolatedClassLoader with additional controls

### Class: `ClassesCollector`

Collects class names from Java source files.

**Package:** `io.github.universetraveller.util`

**Purpose:** Parse Java files to extract class names without compilation.

**Static Methods:**

```java
public static List<String> getClasses(List<File> fileInstances, Pattern pattern)
```
Extract class names from Java source files matching a pattern.

**Parameters:**
- `fileInstances`: List of Java source files
- `pattern`: Regex pattern to match class names

**Returns:** List of fully-qualified class names

**Example:**
```java
import io.github.universetraveller.util.ClassesCollector;
import java.io.File;
import java.util.*;
import java.util.regex.Pattern;

// Find all test classes
List<File> javaFiles = Arrays.asList(
    new File("src/test/MyTest.java"),
    new File("src/test/OtherTest.java")
);

Pattern testPattern = Pattern.compile(".*Test$");
List<String> testClasses = ClassesCollector.getClasses(javaFiles, testPattern);

// testClasses contains: ["com.example.MyTest", "com.example.OtherTest"]
```

### Class: `DevNullPrintStream`

PrintStream that discards all output.

**Package:** `io.github.universetraveller.util`

**Purpose:** Suppress unwanted output during test execution.

**Usage:**
```java
import io.github.universetraveller.util.DevNullPrintStream;

// Suppress System.out
PrintStream original = System.out;
System.setOut(new DevNullPrintStream());

// ... code that produces unwanted output ...

// Restore original
System.setOut(original);
```

### Class: `AntJUnitFormatter`

Formatter for JUnit test results in Ant's XML format.

**Package:** `io.github.universetraveller.util`

**Purpose:** Generate Ant-compatible test result XML.

**Methods:**

```java
public void format(TestResult result, OutputStream out)
```
Format test results as XML.

## Examples

### Example 1: Running Tests Programmatically

```java
import io.github.universetraveller.util.JUnit4Helper;
import org.junit.runner.Result;
import java.util.*;

public class TestRunner {
    public static void main(String[] args) {
        // Define tests to execute
        Map<String, List<String>> testsToRun = new HashMap<>();
        
        // Add test class with specific methods
        testsToRun.put("org.example.MyTest", 
                      Arrays.asList("testAdd", "testSubtract"));
        
        // Add another test class
        testsToRun.put("org.example.OtherTest", 
                      Arrays.asList("testMultiply"));
        
        try {
            // List tests that will be executed
            String testList = JUnit4Helper.listTests(testsToRun);
            System.out.println("Tests to run:\n" + testList);
            
            // Execute tests
            Result result = JUnit4Helper.run(testsToRun);
            
            // Print summary
            System.out.println("\n" + JUnit4Helper.getSummary(result));
            
            // Print failures if any
            if (!result.wasSuccessful()) {
                System.out.println("\n" + 
                    JUnit4Helper.getFailingTestsSummary(result));
            }
            
            // Exit with appropriate code
            System.exit(result.wasSuccessful() ? 0 : 1);
            
        } catch (ClassNotFoundException e) {
            System.err.println("Test class not found: " + e.getMessage());
            System.exit(2);
        }
    }
}
```

### Example 2: Using JUnit Agent

**Compile with Agent:**
```bash
# Build the agent
cd toolkit/junit-agent
mvn clean package

# Run tests with agent
java -javaagent:target/junit-agent-1.0.jar \
     -cp /path/to/junit.jar:/path/to/tests.jar \
     org.junit.runner.JUnitCore com.example.MyTest
```

**Agent Output:**
```
=== Intercepted Assert.fail(String) Calls ===
fail("Expected NullPointerException")
Caused by:
  com.example.MyTest.testNullHandling(MyTest.java:42)
---

fail("Values should be equal")
Caused by:
  com.example.MyTest.testEquality(MyTest.java:58)
---
=== Length: 2 ===
```

### Example 3: Using Isolated ClassLoader

```java
import io.github.universetraveller.util.IsolatedClassLoader;
import java.io.File;
import java.net.URL;
import java.lang.reflect.Method;

public class IsolatedTestExecution {
    public static void main(String[] args) throws Exception {
        // Setup classpath
        URL[] urls = {
            new File("/path/to/project/classes").toURI().toURL(),
            new File("/path/to/project/test-classes").toURI().toURL(),
            new File("/path/to/junit.jar").toURI().toURL()
        };
        
        // Create isolated classloader
        IsolatedClassLoader loader = new IsolatedClassLoader(
            urls,
            ClassLoader.getSystemClassLoader(),
            true,  // parent first for system classes
            false  // not completely isolated
        );
        
        // Add JRE and JUnit to system packages
        loader.addJREPackages();
        loader.addSystemPackageRoot("junit.");
        loader.addSystemPackageRoot("org.junit.");
        
        // Load and execute test
        Class<?> helperClass = loader.loadClass(
            "io.github.universetraveller.util.JUnit4Helper"
        );
        
        Method runMethod = helperClass.getMethod("run", Map.class);
        
        // Define tests
        Map<String, List<String>> tests = new HashMap<>();
        tests.put("com.example.MyTest", Arrays.asList("testMethod"));
        
        // Execute in isolated environment
        Object result = runMethod.invoke(null, tests);
        
        System.out.println("Test executed in isolation: " + result);
    }
}
```

### Example 4: Extracting Classes from Source Files

```java
import io.github.universetraveller.util.ClassesCollector;
import java.io.File;
import java.nio.file.*;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class ClassExtractor {
    public static void main(String[] args) throws Exception {
        // Find all Java files in test directory
        Path testDir = Paths.get("src/test/java");
        List<File> javaFiles = Files.walk(testDir)
            .filter(p -> p.toString().endsWith(".java"))
            .map(Path::toFile)
            .collect(Collectors.toList());
        
        // Pattern to match test classes
        Pattern testPattern = Pattern.compile(".*Test$");
        
        // Extract test class names
        List<String> testClasses = ClassesCollector.getClasses(
            javaFiles, 
            testPattern
        );
        
        // Print results
        System.out.println("Found " + testClasses.size() + " test classes:");
        testClasses.forEach(System.out::println);
    }
}
```

### Example 5: Custom Ant Task Usage

**build.xml:**
```xml
<?xml version="1.0"?>
<project name="example" default="test">
    
    <!-- Define custom tasks -->
    <taskdef name="appendProperty" 
             classname="io.github.universetraveller.ant.AppendProperty"
             classpath="toolkit/classes"/>
    
    <taskdef name="filterPath" 
             classname="io.github.universetraveller.ant.FilterPath"
             classpath="toolkit/classes"/>
    
    <!-- Build classpath incrementally -->
    <property name="cp" value=""/>
    <appendProperty propertyName="cp" value="lib/junit.jar"/>
    <appendProperty propertyName="cp" value="lib/hamcrest.jar"/>
    <appendProperty propertyName="cp" value="build/classes"/>
    
    <!-- Filter to only existing paths -->
    <filterPath pathId="cp" 
                outputProperty="clean.cp" 
                existsOnly="true"/>
    
    <target name="test">
        <echo message="Classpath: ${clean.cp}"/>
    </target>
    
</project>
```

## Building the Toolkit

### Requirements

- Java 8 (JDK 1.8)
- Maven 3.x (for junit-agent)
- Ant 1.9+ (for main toolkit)

### Building JUnit Agent

```bash
cd toolkit/junit-agent
mvn clean package

# Output: target/junit-agent-1.0.jar
```

### Compiling Main Toolkit

```bash
cd toolkit
./compile.sh

# Or manually:
javac -d classes -cp /path/to/ant.jar:other-deps.jar src/**/*.java
```

## Integration Points

### Called from Python

The Python code invokes Java toolkit for:

1. **Property Export**: `Defects4JExport` via Ant
2. **Test Execution**: `Defects4JTest` for running tests
3. **Class Collection**: `ClassesCollector` for finding test classes

**Example Python → Java call:**
```python
# From loaders/project_loader.py
def toolkit_execute(self, prop, proj, wd, xml_attr, main_attr):
    # Constructs command like:
    # ant -buildfile export.xml -Dproperty.name=cp.compile export
    pass
```

### System Properties

The toolkit expects these system properties:

- `c4j.d4j.properties`: Path to Defects4J properties
- `basedir`: Base directory of checked-out bug
- `file.export`: Output file for exported properties

## Performance Considerations

1. **ClassLoader Isolation**: Small overhead but prevents conflicts
2. **Ant Invocation**: Slower than direct Java calls but provides flexibility
3. **Caching**: Python layer caches results to avoid repeated invocations
4. **Simplified Build Files**: Custom build XMLs skip unnecessary compilation

## Best Practices

1. **Use Isolated ClassLoaders**: Prevent class version conflicts
2. **Handle Exceptions**: Wrap ClassNotFoundException and other errors
3. **Clean Up Resources**: Close streams and clear classloaders
4. **Log Appropriately**: Use proper logging instead of System.out
5. **Test in Isolation**: Each test execution should be independent

## Troubleshooting

### ClassNotFoundException

**Cause:** Class not in classpath or wrong classloader.

**Solution:**
- Verify classpath includes all required JARs
- Check classloader delegation settings

### NoSuchMethodError

**Cause:** Multiple versions of same class (e.g., JUnit).

**Solution:**
- Use IsolatedClassLoader
- Add conflicting packages to system package roots

### Build File Errors

**Cause:** Missing Ant targets or properties.

**Solution:**
- Check that required targets exist in build.xml
- Verify all properties are defined before use

## Further Reading

- [Usage Guide](USAGE.md) - Command-line usage documentation
- [Python API](API.md) - Python API documentation
- [Main README](../README.md) - Project overview
- [Toolkit README](../toolkit/README.md) - Toolkit-specific information
