# Java Ant Tasks API

This document covers custom Ant tasks for build automation.

## Overview

CatenaD4J provides custom Ant tasks for property manipulation and build file processing.

Package: `io.github.universetraveller.ant`

## AppendProperty

### Class: `AppendProperty`

Ant task to append a value to an existing property.

**Purpose:** Append to properties with a separator (useful for classpaths).

#### Attributes

- `propertyName` (required): Name of the property to modify
- `value` (required): Value to append
- `sep` (optional): Separator string (default: ":")

#### Build File Usage

```xml
<taskdef name="appendProperty" 
         classname="io.github.universetraveller.ant.AppendProperty"/>

<property name="classpath" value="/path/to/lib1.jar"/>
<appendProperty propertyName="classpath" 
                value="/path/to/lib2.jar" 
                sep=":"/>
<!-- classpath now contains "/path/to/lib1.jar:/path/to/lib2.jar" -->
```

#### Example: Building Classpath

```xml
<project name="example" default="build">
    <taskdef name="appendProperty" 
             classname="io.github.universetraveller.ant.AppendProperty"
             classpath="toolkit/classes"/>
    
    <!-- Initialize empty classpath -->
    <property name="cp" value=""/>
    
    <!-- Add JARs incrementally -->
    <appendProperty propertyName="cp" value="lib/junit.jar"/>
    <appendProperty propertyName="cp" value="lib/hamcrest.jar"/>
    <appendProperty propertyName="cp" value="build/classes"/>
    
    <target name="build">
        <echo message="Classpath: ${cp}"/>
    </target>
</project>
```

## CheckTargetExists

### Class: `CheckTargetExists`

Ant task to check if a target exists in the build file.

**Purpose:** Conditionally execute based on target existence.

#### Attributes

- `target` (required): Target name to check
- `property` (required): Property to set if target exists

#### Build File Usage

```xml
<taskdef name="checkTarget" 
         classname="io.github.universetraveller.ant.CheckTargetExists"/>

<checkTarget target="compile.tests" property="has.test.target"/>

<target name="conditional" if="has.test.target">
    <antcall target="compile.tests"/>
</target>
```

## DynamicNoOpTask

### Class: `DynamicNoOpTask`

Ant task that accepts any attributes but does nothing.

**Purpose:** Stub out tasks during testing or selective execution.

#### Build File Usage

```xml
<taskdef name="noop" 
         classname="io.github.universetraveller.ant.DynamicNoOpTask"/>

<!-- Accepts any attributes, does nothing -->
<noop anything="value" whatever="data" foo="bar"/>
```

## FilterPath

### Class: `FilterPath`

Ant task to filter path elements based on existence or patterns.

**Purpose:** Clean up classpaths by removing non-existent entries.

#### Attributes

- `pathId` (required): Reference ID of path to filter
- `outputProperty` (required): Property to store filtered path
- `existsOnly` (optional): Only include existing files (boolean)

#### Build File Usage

```xml
<taskdef name="filterPath" 
         classname="io.github.universetraveller.ant.FilterPath"/>

<path id="original.classpath">
    <pathelement path="lib/existing.jar"/>
    <pathelement path="lib/missing.jar"/>
    <pathelement path="build/classes"/>
</path>

<filterPath pathId="original.classpath" 
            outputProperty="clean.classpath"
            existsOnly="true"/>

<echo message="Filtered: ${clean.classpath}"/>
```

## CheckAndRename

### Class: `CheckAndRename`

Ant task for conditional file operations.

**Purpose:** Check file existence and perform rename operations.

#### Usage

Check task source code for specific attributes and behavior.

## Complete Example

### build.xml

```xml
<?xml version="1.0"?>
<project name="catena4j-example" default="run">
    
    <!-- Define custom tasks -->
    <taskdef name="appendProperty" 
             classname="io.github.universetraveller.ant.AppendProperty"
             classpath="toolkit/classes"/>
    
    <taskdef name="filterPath" 
             classname="io.github.universetraveller.ant.FilterPath"
             classpath="toolkit/classes"/>
    
    <taskdef name="checkTarget" 
             classname="io.github.universetraveller.ant.CheckTargetExists"
             classpath="toolkit/classes"/>
    
    <!-- Initialize properties -->
    <property name="build.dir" value="build"/>
    <property name="lib.dir" value="lib"/>
    
    <!-- Build classpath incrementally -->
    <property name="cp" value=""/>
    <appendProperty propertyName="cp" value="${lib.dir}/junit-4.12.jar"/>
    <appendProperty propertyName="cp" value="${lib.dir}/hamcrest-core-1.3.jar"/>
    <appendProperty propertyName="cp" value="${build.dir}/classes"/>
    <appendProperty propertyName="cp" value="${build.dir}/test-classes"/>
    
    <!-- Filter to only existing paths -->
    <path id="raw.cp">
        <pathelement path="${cp}"/>
    </path>
    
    <filterPath pathId="raw.cp" 
                outputProperty="clean.cp" 
                existsOnly="true"/>
    
    <!-- Check if optional target exists -->
    <checkTarget target="custom.test" property="has.custom.test"/>
    
    <target name="info">
        <echo message="Raw classpath: ${cp}"/>
        <echo message="Clean classpath: ${clean.cp}"/>
        <echo message="Has custom test: ${has.custom.test}"/>
    </target>
    
    <target name="run" depends="info"/>
    
</project>
```

## Integration with CatenaD4J

These Ant tasks are used internally by CatenaD4J for:

1. **Property Export**: Building classpaths for `cp.compile` and `cp.test`
2. **Build Processing**: Filtering paths to existing files
3. **Target Detection**: Checking for optional build targets

The tasks are invoked by `Defects4JExport` when processing dynamic properties.

## Building

The Ant tasks are compiled as part of the main toolkit:

```bash
cd toolkit
javac -d classes -cp /path/to/ant.jar src/io/github/universetraveller/ant/*.java
```

## Best Practices

1. **Use appendProperty for paths**: Easier than manual string concatenation
2. **Filter paths before use**: Remove non-existent entries to avoid errors
3. **Check targets conditionally**: Use checkTarget before antcall
4. **Minimize noop usage**: Only for testing or controlled scenarios

## Troubleshooting

### Task Not Found

**Cause:** Task not in classpath or wrong classname.

**Solution:**
- Verify classpath in taskdef includes compiled classes
- Check classname is fully qualified

### Property Not Set

**Cause:** appendProperty used before property initialized.

**Solution:**
- Initialize property with empty or default value first
- Use `<property name="var" value=""/>` before appending

## See Also

- [Defects4J Integration](defects4j.md) - Uses these tasks for property export
- [Test Runners](test-runners.md) - Test execution utilities
- [JUnit Agent](junit-agent.md) - Test instrumentation
