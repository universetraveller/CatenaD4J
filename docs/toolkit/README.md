# Java Toolkit Guide

## Overview

The Java toolkit provides performance-critical operations for CatenaD4J through custom Ant tasks and utilities. It bridges the gap between Python's ease of use and Java's integration with existing build systems.

## Architecture

```
Toolkit (toolkit.jar)
├── Ant Tasks (io.github.universetraveller.ant)
│   ├── CheckAndRename
│   ├── AppendProperty
│   ├── CheckTargetExists
│   ├── FilterPath
│   └── DynamicNoOpTask
├── D4J Integration (io.github.universetraveller.d4j)
│   ├── Defects4JExport    (Property export)
│   ├── Defects4JTest      (Test execution)
│   ├── Defects4JExecute   (Ant target execution)
│   └── Support classes
└── Utilities (io.github.universetraveller.util)
    ├── JUnit Helpers (test isolation)
    ├── ClassLoader implementations
    └── Helper utilities
```

## Building the Toolkit

### Using compile.sh

```bash
cd toolkit
bash compile.sh
```

This script:
1. Compiles all `.java` files in `src/`
2. Creates `target/` directory
3. Packages compiled classes into `target/toolkit.jar`

### Manual Build

```bash
cd toolkit

# Create target directory
mkdir -p target

# Compile
javac -cp /path/to/defects4j/major/lib/* \
      -sourcepath ./src \
      -d ./target \
      src/io/github/universetraveller/**/*.java

# Package
jar cf ./target/toolkit.jar -C ./target .
```

### Using setup_unix_user.py

```bash
python3 setup_unix_user.py -n c4j
```

This automatically:
1. Builds the toolkit
2. Generates startup script
3. Adds to PATH

## Ant Tasks

Custom Ant tasks for build file processing.

### CheckAndRename

Check if a file/directory exists and rename it.

**Usage**:
```xml
<taskdef name="checkAndRename" 
         classname="io.github.universetraveller.ant.CheckAndRename"
         classpathref="d4j.classpath"/>

<checkAndRename from="${old.path}" 
                to="${new.path}" 
                check="${check.path}"/>
```

**Attributes**:
- `from`: Source path to rename
- `to`: Destination path
- `check`: Path to check for existence (only rename if this exists)

**Example**:
```xml
<!-- Backup build.xml if it exists -->
<checkAndRename from="build.xml" 
                to="build.xml.bak" 
                check="build.xml"/>
```

### AppendProperty

Append a value to a property with a separator.

**Usage**:
```xml
<taskdef name="appendProperty" 
         classname="io.github.universetraveller.ant.AppendProperty"
         classpathref="d4j.classpath"/>

<appendProperty name="classpath" 
                value="${new.jar}" 
                separator=":"/>
```

**Attributes**:
- `name`: Property name
- `value`: Value to append
- `separator`: Separator character (default: ',')

**Example**:
```xml
<!-- Build classpath incrementally -->
<appendProperty name="compile.classpath" value="lib/commons.jar" separator=":"/>
<appendProperty name="compile.classpath" value="lib/junit.jar" separator=":"/>
<!-- Result: lib/commons.jar:lib/junit.jar -->
```

### CheckTargetExists

Check if an Ant target exists in the project.

**Usage**:
```xml
<taskdef name="checkTargetExists" 
         classname="io.github.universetraveller.ant.CheckTargetExists"
         classpathref="d4j.classpath"/>

<checkTargetExists target="test" property="test.exists"/>

<condition property="run.tests">
    <isset property="test.exists"/>
</condition>
```

**Attributes**:
- `target`: Target name to check
- `property`: Property to set if target exists

### FilterPath

Filter path elements based on file existence.

**Usage**:
```xml
<taskdef name="filterPath" 
         classname="io.github.universetraveller.ant.FilterPath"
         classpathref="d4j.classpath"/>

<path id="source.path">
    <pathelement location="src/main/java"/>
    <pathelement location="src/java"/>  <!-- May not exist -->
</path>

<filterPath pathid="source.path" outputid="filtered.source.path"/>
<!-- Result: Only existing directories in filtered.source.path -->
```

**Attributes**:
- `pathid`: ID of path to filter
- `outputid`: ID for filtered result path

### DynamicNoOpTask

Placeholder task that does nothing. Used for dynamic task resolution.

**Usage**:
```xml
<taskdef name="noop" 
         classname="io.github.universetraveller.ant.DynamicNoOpTask"
         classpathref="d4j.classpath"/>

<noop/>  <!-- Does nothing -->
```

Useful for:
- Default implementations of optional targets
- Placeholder targets in dynamic build files

## Defects4J Integration

### Defects4JExport

Export Defects4J properties efficiently.

**Class**: `io.github.universetraveller.d4j.Defects4JExport`

**Usage**:
```bash
java -cp toolkit.jar:defects4j/major/lib/*:... \
     -Dc4j.d4j.properties=/path/to/defects4j.properties \
     -Dbasedir=/working/directory \
     io.github.universetraveller.d4j.Defects4JExport \
     /path/to/build.xml \
     <property_name> \
     [output_file]
```

**Arguments**:
1. Build XML file path
2. Property name to export
3. Output file (optional, defaults to stdout)

**System Properties**:
- `c4j.d4j.properties`: Path to Defects4J properties file
- `basedir`: Working directory (project base)

**Supported Properties**:

*Dynamic Properties*:
- `cp.compile`: Compilation classpath
- `cp.test`: Test classpath
- `dir.bin.classes`: Compiled classes directory
- `dir.bin.tests`: Compiled test classes directory
- `tests.all`: All test classes

*Static Properties* (also supported):
- `classes.modified`
- `classes.relevant`
- `tests.trigger`
- `tests.relevant`
- `dir.src.classes`
- `dir.src.tests`

**Examples**:
```bash
# Export compile classpath
java -cp ... Defects4JExport build.xml cp.compile

# Export all tests to file
java -cp ... Defects4JExport build.xml tests.all /tmp/tests.txt

# Export modified classes
java -cp ... Defects4JExport build.xml classes.modified
```

### Defects4JTest

Run JUnit tests with custom isolation levels.

**Class**: `io.github.universetraveller.d4j.Defects4JTest`

**Usage**:
```bash
java -cp toolkit.jar:defects4j/major/lib/*:... \
     -Dc4j.d4j.properties=/path/to/defects4j.properties \
     -Dbasedir=/working/directory \
     -DOUTFILE=/path/to/failing_tests \
     -Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper \
     io.github.universetraveller.d4j.Defects4JTest \
     /path/to/build.xml \
     [test1] [test2] ...
```

**Arguments**:
1. Build XML file path
2. Test classes/methods to run (optional; if omitted, runs all tests)

**System Properties**:
- `c4j.d4j.properties`: Defects4J properties
- `basedir`: Working directory
- `OUTFILE`: File to write failing tests
- `c4j.tests.printer.out`: File to list all tests (list mode)
- `c4j.test.helper`: Test helper class (for isolation level 1 or 2)
- `c4j.test.runner`: Set to 'ant' for isolation level 3

**Test Format**:
- Class: `org.example.TestClass`
- Method: `org.example.TestClass#testMethod`

**Isolation Levels**:

**Level 1** (default): Reused isolated classloader
```bash
-Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper
```
- Fastest execution
- Single classloader for all tests
- Good isolation from system classpath

**Level 2**: Per-class isolated classloader
```bash
-Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper1
```
- New classloader for each test class
- Better isolation
- Slight performance overhead

**Level 3**: Ant's JUnit task
```bash
-Dc4j.test.runner=ant
```
- Uses standard Ant JUnit runner
- Maximum isolation
- Highest overhead

**Examples**:
```bash
# Run all tests (level 1)
java -cp ... \
     -Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper \
     -DOUTFILE=/tmp/failing_tests \
     Defects4JTest build.xml

# Run specific test
java -cp ... \
     -Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper \
     -DOUTFILE=/tmp/failing_tests \
     Defects4JTest build.xml org.example.MyTest#testMethod

# List all tests (don't run)
java -cp ... \
     -Dc4j.tests.printer.out=/tmp/all_tests \
     Defects4JTest build.xml

# Run with maximum isolation
java -cp ... \
     -Dc4j.test.runner=ant \
     -DOUTFILE=/tmp/failing_tests \
     Defects4JTest build.xml
```

### Defects4JExecute

Execute arbitrary Ant targets.

**Class**: `io.github.universetraveller.d4j.Defects4JExecute`

**Usage**:
```bash
java -cp toolkit.jar:defects4j/major/lib/*:... \
     -Dc4j.d4j.properties=/path/to/defects4j.properties \
     -Dbasedir=/working/directory \
     io.github.universetraveller.d4j.Defects4JExecute \
     /path/to/build.xml \
     <target_name>
```

**Arguments**:
1. Build XML file path
2. Ant target name

**Examples**:
```bash
# Compile classes
java -cp ... Defects4JExecute build.xml compile

# Compile tests
java -cp ... Defects4JExecute build.xml compile.tests

# Clean build
java -cp ... Defects4JExecute build.xml clean
```

## Test Utilities

### JUnit Helpers

Custom JUnit runners with classloader isolation.

#### JUnit4Helper (Level 1)

**Class**: `io.github.universetraveller.util.JUnit4Helper`

**Features**:
- Reused isolated classloader
- Fastest performance
- Good isolation

**Usage**:
```bash
java -cp ... \
     -Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper \
     ... Defects4JTest build.xml
```

#### JUnit4Helper1 (Level 2)

**Class**: `io.github.universetraveller.util.JUnit4Helper1`

**Features**:
- New classloader per test class
- Better isolation
- Slight performance cost

**Usage**:
```bash
java -cp ... \
     -Dc4j.test.helper=io.github.universetraveller.util.JUnit4Helper1 \
     ... Defects4JTest build.xml
```

#### JUnit3Helper

**Class**: `io.github.universetraveller.util.JUnit3Helper`

**Features**:
- JUnit 3 compatibility
- Similar isolation to JUnit4Helper

**Usage**: Automatically selected for JUnit 3 tests

### ClassLoader Utilities

#### IsolatedClassLoader

**Class**: `io.github.universetraveller.util.IsolatedClassLoader`

Custom classloader for test isolation.

**Key Features**:
- Loads test classes in isolation
- Prevents system classpath contamination
- Used by JUnit helpers

**Constructor**:
```java
public IsolatedClassLoader(URL[] urls, ClassLoader parent)
```

#### ControlledURLClassLoader

**Class**: `io.github.universetraveller.util.ControlledURLClassLoader`

More fine-grained classloader control.

### Test Collection

#### ClassesCollector

**Class**: `io.github.universetraveller.util.ClassesCollector`

Collect test classes from filesystem.

**Methods**:
```java
public static List<String> collectTestClasses(File dir, String pattern)
```

Scans directory for test classes matching pattern.

## JUnit Agent (EXPERIMENTAL)

⚠️ **WARNING: EXPERIMENTAL FEATURE** ⚠️

**Location**: `toolkit/junit-agent/`

**Status**: Not integrated into main toolkit; experimental only

**Purpose**: 
- Prevent failed assertions from halting test execution
- Collect all assertion failures in a single test run
- Preserve exception messages and stack traces

**Potential Use Cases**:
- Advanced fault localization
- Comprehensive test failure analysis
- Research applications

**Current Status**:
- Implementation exists but not production-ready
- Not loaded by default
- Requires additional testing and validation

**Future Plans**:
- May be integrated for advanced testing features
- Currently available for research purposes only

## Integration with Python

### Python Invocation

Python code invokes toolkit via `toolkit_execute()`:

```python
from catena4j.util import toolkit_execute

result = toolkit_execute(
    target='tests.all',
    project='Chart',
    wd='./workspace',
    xml_attr='c4j_rel_project_export_xml',
    main_attr='c4j_toolkit_export_main',
    context=context
)
```

This constructs and executes:
```bash
java -cp toolkit.jar:defects4j/... \
     -Dc4j.d4j.properties=... \
     -Dbasedir=./workspace \
     io.github.universetraveller.d4j.Defects4JExport \
     Chart.export.xml \
     tests.all
```

### Configuration

Toolkit configuration in `catena4j/config.py`:

```python
c4j_rel_toolkit_lib = 'toolkit/target/toolkit.jar'
c4j_toolkit_export_main = 'io.github.universetraveller.d4j.Defects4JExport'
c4j_toolkit_execute_main = 'io.github.universetraveller.d4j.Defects4JExecute'
c4j_toolkit_test_main = 'io.github.universetraveller.d4j.Defects4JTest'
```

## Build Files

Each project has custom build files:

```
projects/<Project>/
├── <Project>.export.xml     # For property export
├── <Project>.compile.xml    # For compilation
└── <Project>.test.xml       # For testing (optional)
```

These simplified build files:
- Skip unnecessary Defects4J targets
- Include only required dependencies
- Use custom tasks for optimization

**Example** (`Chart.export.xml`):
```xml
<?xml version="1.0"?>
<project name="Chart-Export" basedir="." default="export.cp.compile">
    <!-- Simplified build file for property export -->
    
    <taskdef name="filterPath" 
             classname="io.github.universetraveller.ant.FilterPath"
             classpathref="d4j.classpath"/>
    
    <target name="export.cp.compile">
        <path id="compile.path">
            <pathelement location="${classes.dir}"/>
            <fileset dir="${lib.dir}">
                <include name="**/*.jar"/>
            </fileset>
        </path>
        
        <filterPath pathid="compile.path" outputid="filtered.path"/>
        
        <pathconvert property="cp.compile" refid="filtered.path"/>
        <echo message="${cp.compile}" file="${file.export}"/>
    </target>
</project>
```

## Performance Considerations

### JVM Startup Overhead

Each toolkit invocation starts a new JVM:
- Startup time: ~200-500ms
- Memory overhead: ~50-100MB

**Mitigation**:
- Cache results when possible
- Batch operations
- Use lazy evaluation

### Build File Processing

Ant parses and executes build files:
- Parsing time: ~100-200ms
- Execution time: varies by target

**Optimization**:
- Simplified build files (skip unnecessary targets)
- Minimal dependency resolution
- Custom tasks for common operations

### Classpath Construction

Large classpaths slow initialization:
- Defects4J libs: ~50 JARs
- Project dependencies: varies

**Optimization**:
- Use wildcard classpath (`lib/*`)
- Minimize classpath length
- Filter non-existent paths

## Extending the Toolkit

### Adding Custom Ant Tasks

1. **Create Task Class**:
```java
package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;
import org.apache.tools.ant.BuildException;

public class MyCustomTask extends Task {
    private String parameter;
    
    public void setParameter(String parameter) {
        this.parameter = parameter;
    }
    
    @Override
    public void execute() throws BuildException {
        // Task logic
        log("Executing with parameter: " + parameter);
    }
}
```

2. **Compile and Package**:
```bash
cd toolkit
bash compile.sh
```

3. **Use in Build Files**:
```xml
<taskdef name="mycustom" 
         classname="io.github.universetraveller.ant.MyCustomTask"
         classpathref="d4j.classpath"/>

<mycustom parameter="value"/>
```

### Adding Main Classes

1. **Create Main Class**:
```java
package io.github.universetraveller.d4j;

public class MyCustomMain extends Defects4JStartup {
    public static void main(String[] args) {
        // Initialization
        MyCustomMain instance = new MyCustomMain(args[0]);
        
        // Logic
        String result = instance.process(args[1]);
        
        // Output
        System.out.println(result);
    }
    
    public MyCustomMain(String buildFile) {
        super();
        initializeProjectHelper2();
        initializeDefects4J(
            System.getProperty("c4j.d4j.properties"),
            System.getProperty("basedir")
        );
        projectHelper.parse(project, new File(buildFile));
    }
    
    public String process(String input) {
        // Custom processing
        return "Result: " + input;
    }
}
```

2. **Invoke from Python**:
```python
from catena4j.util import toolkit_execute

result = toolkit_execute(
    target='input_value',
    project='Chart',
    wd='./workspace',
    xml_attr='c4j_rel_project_export_xml',
    main_attr='my_custom_main',  # Configure in config.py
    context=context
)
```

## Troubleshooting

### Compilation Errors

**Issue**: `javac: command not found`

**Solution**: Ensure JDK 8 is installed and in PATH:
```bash
java -version  # Should show 1.8.x
javac -version  # Should show 1.8.x
```

### ClassNotFoundException

**Issue**: `java.lang.ClassNotFoundException: ...`

**Solution**: Check classpath includes:
- `toolkit.jar`
- Defects4J Ant libraries
- All necessary dependencies

### Ant Task Not Found

**Issue**: `Could not create task or type of type: mytask`

**Solution**: 
1. Ensure task is compiled into `toolkit.jar`
2. Check `taskdef` uses correct classname
3. Verify classpath includes `toolkit.jar`

### OutOfMemoryError

**Issue**: `java.lang.OutOfMemoryError: Java heap space`

**Solution**: Increase heap size:
```python
toolkit_execute(..., java_options=['-Xmx2g'])
```

## Best Practices

### DO

✅ Use simplified build files for performance
✅ Filter paths to remove non-existent entries
✅ Cache expensive property computations
✅ Use appropriate isolation level for tests
✅ Recompile toolkit after modifications

### DON'T

❌ Don't use full Defects4J build files (too slow)
❌ Don't start multiple JVMs when one suffices
❌ Don't include unnecessary dependencies in classpath
❌ Don't use experimental features in production
❌ Don't forget to rebuild after Java changes

## See Also

- [Architecture](../ARCHITECTURE.md) - Python-Java integration design
- [Utilities Guide](../utilities/README.md) - toolkit_execute() usage
- [Commands Guide](../commands/README.md) - How commands use toolkit
