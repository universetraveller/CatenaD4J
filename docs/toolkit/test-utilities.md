# Test Utilities

JUnit test runners and isolation utilities.


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

