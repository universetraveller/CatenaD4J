# Ant Tasks

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

