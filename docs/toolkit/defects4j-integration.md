# Defects4J Integration

Integration components for Defects4J infrastructure.


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

