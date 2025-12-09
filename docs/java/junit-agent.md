# Java JUnit Agent API

This document covers the JUnit agent for bytecode instrumentation and test interception.

## Overview

The JUnit Agent is a Java agent that instruments JUnit tests to intercept and record failure information without modifying test code.

Package: `io.github.universetraveller.junit.agent`

## JUnitAgent

### Class: `JUnitAgent`

Java agent that instruments JUnit Assert.fail() calls.

**Purpose:** Intercept JUnit assertions to track failure locations and messages.

#### Agent Entry Point

```java
public static void premain(String agentArgs, Instrumentation inst)
```
Entry point called by JVM when agent is loaded.

**Parameters:**
- `agentArgs`: Agent arguments (unused)
- `inst`: Instrumentation instance

#### Usage

```bash
java -javaagent:/path/to/junit-agent.jar -jar your-tests.jar
```

#### Features

- Intercepts `Assert.fail(String)` calls
- Records failure messages and stack traces
- Prints detailed failure information on shutdown
- No modification to test code required

#### Output Format

```
=== Intercepted Assert.fail(String) Calls ===
fail("Expected exception not thrown")
Caused by:
  com.example.MyTest.testException(MyTest.java:42)
  ...
---
=== Length: 1 ===
```

#### Example

```bash
# Build the agent
cd toolkit/junit-agent
mvn clean package

# Run tests with agent
java -javaagent:target/junit-agent-1.0.jar \
     -cp /path/to/junit.jar:/path/to/tests.jar \
     org.junit.runner.JUnitCore com.example.MyTest
```

## JUnitRecorder

### Class: `JUnitRecorder`

Records test failure information captured by the agent.

**Purpose:** Thread-safe storage for failure records.

#### Inner Class: `FailureRecord`

```java
public static class FailureRecord {
    public final String message;
    public final List<String> userStack;
    
    public FailureRecord(String message, List<String> userStack)
}
```

**Fields:**
- `message`: Failure message from Assert.fail()
- `userStack`: Stack trace from user code (filtered)

#### Methods

```java
public static void record(String message, List<String> userStack)
```
Record a test failure with message and stack trace.

**Parameters:**
- `message`: Failure message
- `userStack`: Filtered stack trace

```java
public static List<FailureRecord> getFailures()
```
Get all recorded failures.

**Returns:** List of FailureRecord objects

```java
public static void clear()
```
Clear all recorded failures.

#### Example

```java
import io.github.universetraveller.junit.agent.JUnitRecorder;
import io.github.universetraveller.junit.agent.JUnitRecorder.FailureRecord;
import java.util.List;

// Get failures after test execution
List<FailureRecord> failures = JUnitRecorder.getFailures();

for (FailureRecord record : failures) {
    System.out.println("Message: " + record.message);
    System.out.println("Stack:");
    for (String frame : record.userStack) {
        System.out.println("  " + frame);
    }
}

// Clear for next run
JUnitRecorder.clear();
```

## JUnitTransformer

### Class: `JUnitTransformer`

Bytecode transformer for instrumenting JUnit classes.

**Purpose:** Transform Assert.fail() calls to record failures.

#### Installation

```java
public static void install(Instrumentation inst)
```
Install the transformer into the JVM.

**Parameters:**
- `inst`: Instrumentation instance

**Note:** Called automatically by JUnitAgent.premain()

## JUnitInterceptor

### Class: `JUnitInterceptor`

Interceptor methods called from instrumented code.

**Purpose:** Provide interception points for transformed bytecode.

**Note:** Internal implementation class, not meant for direct use.

## Building the Agent

### Requirements

- Java 8 (JDK 1.8)
- Maven 3.x

### Build Steps

```bash
cd toolkit/junit-agent
mvn clean package

# Output: target/junit-agent-1.0.jar
```

### Maven Configuration

The agent is built with the following key configuration:

```xml
<manifestEntries>
    <Premain-Class>io.github.universetraveller.junit.agent.JUnitAgent</Premain-Class>
    <Can-Retransform-Classes>true</Can-Retransform-Classes>
</manifestEntries>
```

## Complete Example

### Test Class

```java
package com.example;

import org.junit.Test;
import static org.junit.Assert.fail;

public class MyTest {
    @Test
    public void testFailure() {
        fail("This test always fails");
    }
    
    @Test
    public void testException() {
        try {
            // Some code that should throw
            processData(null);
            fail("Expected NullPointerException");
        } catch (NullPointerException e) {
            // Expected
        }
    }
    
    private void processData(Object data) {
        if (data == null) {
            throw new NullPointerException();
        }
    }
}
```

### Running with Agent

```bash
# Compile test
javac -cp junit-4.12.jar com/example/MyTest.java

# Run with agent
java -javaagent:junit-agent-1.0.jar \
     -cp .:junit-4.12.jar:hamcrest-core-1.3.jar \
     org.junit.runner.JUnitCore com.example.MyTest
```

### Expected Output

```
JUnit version 4.12
.E.E
Time: 0.005

There were 2 failures:
1) testFailure(com.example.MyTest)
java.lang.AssertionError: This test always fails
    at org.junit.Assert.fail(Assert.java:88)
    ...

2) testException(com.example.MyTest)
java.lang.AssertionError: Expected NullPointerException
    ...

FAILURES!!!
Tests run: 2,  Failures: 2

=== Intercepted Assert.fail(String) Calls ===
fail("This test always fails")
Caused by:
  com.example.MyTest.testFailure(MyTest.java:9)
---
fail("Expected NullPointerException")
Caused by:
  com.example.MyTest.testException(MyTest.java:17)
---
=== Length: 2 ===
```

## Use Cases

1. **Failure Analysis**: Understand where and why tests are failing
2. **Debugging**: Track assertion failures without modifying code
3. **Test Reporting**: Generate custom failure reports
4. **Research**: Analyze test failure patterns

## Best Practices

1. **Use for analysis only**: Don't rely on agent for production
2. **Check compatibility**: Ensure JUnit version is compatible
3. **Filter stack traces**: Agent filters internal frames automatically
4. **Thread safety**: Recorder uses concurrent data structures

## Troubleshooting

### Agent Not Loading

**Cause:** Incorrect agent JAR path or format.

**Solution:**
- Verify JAR file exists
- Check MANIFEST.MF has correct Premain-Class

### No Output Generated

**Cause:** No Assert.fail() calls in tests.

**Solution:**
- Verify tests use Assert.fail()
- Check that shutdown hook runs

### ClassNotFoundException

**Cause:** JUnit not in classpath.

**Solution:**
- Add JUnit JAR to classpath
- Ensure correct JUnit version

## See Also

- [Test Runners](test-runners.md) - JUnit test execution
- [Defects4J Integration](defects4j.md) - Property export
- [Ant Tasks](ant-tasks.md) - Build integration
