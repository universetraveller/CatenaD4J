# Java Defects4J Integration API

This document covers classes for integrating with Defects4J and exporting properties.

## Overview

The Defects4J integration classes provide property export functionality and test execution for CatenaD4J bugs.

Package: `io.github.universetraveller.d4j`

## Defects4JExport

### Class: `Defects4JExport`

Exports static and dynamic properties for Defects4J bugs.

**Purpose:** Export version-specific properties like classpaths, test lists, and directory paths.

#### Constructors

```java
public Defects4JExport(String projectBuildFile)
```
Initialize with a project build file path.

**Parameters:**
- `projectBuildFile`: Path to the Ant build.xml file

**System Properties Required:**
- `c4j.d4j.properties`: Path to Defects4J properties file
- `basedir`: Base directory of the project

#### Property Types

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

#### Example

```java
// Set required system properties
System.setProperty("c4j.d4j.properties", "/path/to/defects4j.properties");
System.setProperty("basedir", "/path/to/project");

// Create exporter
Defects4JExport exporter = new Defects4JExport("/path/to/build.xml");

// Export is typically invoked via Ant tasks or Python code
```

## Defects4JStartup

### Class: `Defects4JStartup`

Base class for Defects4J integration providing initialization.

**Extends:** org.apache.tools.ant.Project

**Purpose:** Initialize project infrastructure and manage Ant build environment.

#### Protected Methods

```java
protected void initializeDefects4J(String propertiesFile, String baseDir)
```
Initialize Defects4J properties and environment.

**Parameters:**
- `propertiesFile`: Path to defects4j.properties
- `baseDir`: Base directory of project

```java
protected void initializeProjectHelper2()
```
Initialize Ant ProjectHelper for build file processing.

## Defects4JTest

### Class: `Defects4JTest`

Minimal test runner for executing JUnit tests in isolation.

**Extends:** AbstractDefects4JTest

**Purpose:** Execute developer-written tests with isolated classloaders.

#### Methods

```java
public void initializeClassLoader(String[] pathElements) throws MalformedURLException
```
Initialize an isolated classloader with specified classpath.

**Parameters:**
- `pathElements`: Array of classpath entries

#### Features

- Isolated classloader prevents class conflicts
- Supports both JUnit 3 and JUnit 4
- Minimal overhead compared to Ant junit task
- Abort-on-failure capability (in subclasses)

#### Example

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

## AbstractDefects4JTest

### Class: `AbstractDefects4JTest`

Abstract base for test execution with common functionality.

**Purpose:** Provide common test execution infrastructure.

**Abstract:** Yes

## Defects4JExecute

### Class: `Defects4JExecute`

Main entry point for executing Defects4J-related operations.

**Purpose:** Execute export or test operations from command line.

#### Main Method

```java
public static void main(String[] args)
```

Entry point for command-line execution.

## Property Export Process

### Static Properties

Static properties are read directly from Defects4J metadata files without requiring project compilation:

1. Python code calls `export.py`
2. `export.py` uses `d4jutil.py` to read metadata
3. Metadata is cached in properties files
4. Results returned to user

### Dynamic Properties

Dynamic properties require processing the project's build file:

1. Python code invokes Ant with export target
2. Ant loads simplified build.xml
3. Custom Ant tasks (AppendProperty, FilterPath) process classpath
4. Defects4JExport outputs property value
5. Python reads output and caches result

### Example: Exporting cp.compile

```bash
# Python invokes:
ant -f /tmp/export.xml \
    -Dc4j.d4j.properties=/path/to/defects4j.properties \
    -Dbasedir=/path/to/project \
    -Dfile.export=/tmp/output.txt \
    export.cp.compile

# build.xml contains:
<target name="export.cp.compile">
    <appendProperty propertyName="cp" value="${classes.dir}"/>
    <appendProperty propertyName="cp" value="${lib.dir}/junit.jar"/>
    <filterPath pathId="cp" outputProperty="clean.cp" existsOnly="true"/>
    <echo message="${clean.cp}" file="${file.export}"/>
</target>
```

## Complete Example

### Using from Python

```python
from catena4j.loaders import get_project_loader
from catena4j.dispatcher import ExecutionContext

context = ExecutionContext()
loader = get_project_loader('Chart')(context)

# This internally uses Defects4JExport via Ant
classpath = loader.toolkit_execute(
    'cp.compile',
    'Chart',
    '/tmp/chart15',
    xml_attr='c4j_rel_project_export_xml',
    main_attr='c4j_toolkit_export_main'
)

print(f"Compile classpath: {classpath}")
```

### Using from Java

```java
import io.github.universetraveller.d4j.Defects4JExport;

public class PropertyExporter {
    public static void main(String[] args) {
        // Set system properties
        System.setProperty("c4j.d4j.properties", 
            "/home/user/.defects4j/defects4j.properties");
        System.setProperty("basedir", "/tmp/chart15");
        System.setProperty("file.export", "/tmp/output.txt");
        
        // Create exporter with build file
        Defects4JExport exporter = new Defects4JExport(
            "/tmp/chart15/build.xml"
        );
        
        // Properties are exported via Ant targets
        // Results written to file.export
    }
}
```

## Performance Considerations

1. **Static properties**: Fast (read from cached metadata)
2. **Dynamic properties**: Slower (requires Ant processing)
3. **Caching**: Python layer caches results to avoid repeated invocations
4. **Simplified build files**: Custom XMLs skip unnecessary compilation

## Best Practices

1. **Cache dynamic properties**: Use `--from-cache` flag in export command
2. **Minimize Ant invocations**: Batch property requests when possible
3. **Use static when available**: Prefer static over dynamic properties
4. **Handle errors**: Check for build failures and missing properties

## Troubleshooting

### Build File Not Found

**Cause:** Incorrect build.xml path.

**Solution:**
- Verify path is absolute and correct
- Check file exists and is readable

### Property Not Found

**Cause:** Target missing in build file.

**Solution:**
- Ensure export target exists for property
- Check property name is correct

### Classpath Empty

**Cause:** All paths filtered out or missing dependencies.

**Solution:**
- Check that required JARs exist
- Verify paths in build configuration

## See Also

- [Test Runners](test-runners.md) - JUnit test execution
- [Ant Tasks](ant-tasks.md) - Custom Ant tasks used for export
- [JUnit Agent](junit-agent.md) - Test instrumentation
- [Python Commands API](../python/commands.md) - Python export command
