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
- [Utilities Guide](../utilities.md) - toolkit_execute() usage
- [Commands Guide](../commands.md) - How commands use toolkit
