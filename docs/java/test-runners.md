# Java Test Runners API

This document covers test execution utilities in the Java toolkit.

## Overview

The test runners provide programmatic execution of JUnit 3 and JUnit 4 tests with isolated classloaders to prevent conflicts.

Package: `io.github.universetraveller.util`

## JUnit 4 Test Runner

### Class: `JUnit4Helper`

Helper for executing JUnit 4 tests programmatically.

**Package:** `io.github.universetraveller.util`

#### Static Methods

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

**Returns:** Summary like "Run X tests in Y ms; ignore Z tests; W tests failed --- PASS/FAIL"

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

#### Example

```java
import io.github.universetraveller.util.JUnit4Helper;
import org.junit.runner.Result;
import java.util.*;

public class TestRunner {
    public static void main(String[] args) throws Exception {
        // Define tests to run
        Map<String, List<String>> tests = new HashMap<>();
        tests.put("com.example.MyTest", 
                 Arrays.asList("testMethod1", "testMethod2"));
        tests.put("com.example.OtherTest", 
                 Arrays.asList("testMethod3"));
        
        // Execute tests
        Result result = JUnit4Helper.run(tests);
        
        // Print summary
        System.out.println(JUnit4Helper.getSummary(result));
        
        // Print failures if any
        if (!result.wasSuccessful()) {
            System.out.println(JUnit4Helper.getFailingTestsSummary(result));
        }
        
        // Exit with appropriate code
        System.exit(result.wasSuccessful() ? 0 : 1);
    }
}
```

## JUnit 3 Test Runner

### Class: `JUnit3Helper`

Helper for executing JUnit 3 TestCase-based tests.

**Package:** `io.github.universetraveller.util`

#### Static Methods

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

#### Example

```java
import io.github.universetraveller.util.JUnit3Helper;
import junit.framework.TestResult;
import java.util.*;

Map<String, List<String>> tests = new HashMap<>();
tests.put("com.example.LegacyTest", Arrays.asList("testOldStyle"));

TestResult result = JUnit3Helper.run(tests);
System.out.println(JUnit3Helper.getSummary(result));
```

## ClassLoader Isolation

### Class: `IsolatedClassLoader`

ClassLoader that isolates loaded classes from parent classloader.

**Package:** `io.github.universetraveller.util`

**Extends:** URLClassLoader

**Purpose:** Prevent class conflicts by loading classes in isolation.

#### Constructor

```java
public IsolatedClassLoader(URL[] urls, ClassLoader parent, 
                          boolean parentFirst, boolean isolated)
```

**Parameters:**
- `urls`: Classpath URLs
- `parent`: Parent classloader
- `parentFirst`: Whether to delegate to parent first
- `isolated`: Whether to fully isolate from parent

#### Methods

```java
public void addJREPackages()
```
Add JRE packages to system packages list.

```java
public void addSystemPackageRoot(String packageRoot)
```
Add a package prefix to load from system classloader.

**Parameters:**
- `packageRoot`: Package prefix (e.g., "org.junit.")

#### Example

```java
import io.github.universetraveller.util.IsolatedClassLoader;
import java.io.File;
import java.net.URL;

// Setup classpath
URL[] urls = {
    new File("/path/to/classes").toURI().toURL(),
    new File("/path/to/junit.jar").toURI().toURL()
};

// Create isolated classloader
IsolatedClassLoader loader = new IsolatedClassLoader(
    urls,
    ClassLoader.getSystemClassLoader(),
    true,  // parent first for system classes
    false  // not completely isolated
);

// Load JUnit from system classloader
loader.addJREPackages();
loader.addSystemPackageRoot("junit.");
loader.addSystemPackageRoot("org.junit.");

// Load test class in isolation
Class<?> testClass = loader.loadClass("com.example.MyTest");
```

### Class: `ControlledURLClassLoader`

URLClassLoader with fine-grained control over class loading.

**Package:** `io.github.universetraveller.util`

**Purpose:** Advanced classloader with explicit control over delegation.

Similar to IsolatedClassLoader with additional control mechanisms.

## Additional Utilities

### Class: `ClassesCollector`

Collects class names from Java source files without compilation.

**Package:** `io.github.universetraveller.util`

#### Static Methods

```java
public static List<String> getClasses(List<File> fileInstances, Pattern pattern)
```
Extract class names from Java source files matching a pattern.

**Parameters:**
- `fileInstances`: List of Java source files
- `pattern`: Regex pattern to match class names

**Returns:** List of fully-qualified class names

#### Example

```java
import io.github.universetraveller.util.ClassesCollector;
import java.io.File;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.nio.file.*;

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

System.out.println("Found " + testClasses.size() + " test classes");
testClasses.forEach(System.out::println);
```

### Class: `DevNullPrintStream`

PrintStream that discards all output.

**Package:** `io.github.universetraveller.util`

**Purpose:** Suppress unwanted output during test execution.

#### Example

```java
import io.github.universetraveller.util.DevNullPrintStream;
import java.io.PrintStream;

// Suppress System.out
PrintStream original = System.out;
System.setOut(new DevNullPrintStream());

// ... code that produces unwanted output ...

// Restore original
System.setOut(original);
```

## Complete Example: Running Tests in Isolation

```java
import io.github.universetraveller.util.*;
import java.io.File;
import java.net.URL;
import java.lang.reflect.Method;
import java.util.*;

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
        
        // Load helper class through isolated loader
        Class<?> helperClass = loader.loadClass(
            "io.github.universetraveller.util.JUnit4Helper"
        );
        
        // Get run method
        Method runMethod = helperClass.getMethod("run", Map.class);
        
        // Define tests
        Map<String, List<String>> tests = new HashMap<>();
        tests.put("com.example.MyTest", Arrays.asList("testMethod"));
        
        // Execute in isolated environment
        Object result = runMethod.invoke(null, tests);
        
        // Get summary
        Method summaryMethod = helperClass.getMethod("getSummary", 
            Class.forName("org.junit.runner.Result"));
        String summary = (String) summaryMethod.invoke(null, result);
        
        System.out.println("Test executed in isolation: " + summary);
    }
}
```

## Best Practices

1. **Use isolated classloaders**: Prevent class version conflicts
2. **Handle exceptions properly**: Wrap ClassNotFoundException and others
3. **Clean up resources**: Close streams and clear classloaders
4. **Test in isolation**: Each test execution should be independent
5. **Specify system packages**: Add JRE and framework packages to system list

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

## See Also

- [JUnit Agent](junit-agent.md) - Test instrumentation and interception
- [Defects4J Integration](defects4j.md) - Property export and integration
- [Ant Tasks](ant-tasks.md) - Build system integration
