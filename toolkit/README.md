# CatenaD4J Toolkit

## Build System

The toolkit now uses **Gradle with wrapper** for building, which eliminates the need for users to install Gradle manually. The wrapper downloads and uses the correct Gradle version automatically.

### Building the Toolkit

```bash
# Using the Gradle wrapper (recommended)
./gradlew clean build

# Or using the compile.sh script
./compile.sh
```

The build produces `target/toolkit.jar` which contains all compiled classes.

### Dependencies

The toolkit depends on:
- Apache Ant 1.10.14 (for build tasks)
- Apache Ant JUnit 1.10.14 (for JUnit integration)
- JUnit 4.13.2 (for test runner support)

All dependencies are managed by Gradle and downloaded automatically.

### Java Version Compatibility

**Current target:** Java 8 (for maximum compatibility)

**Future migration to Java 11:** The build system is prepared for Java 11+ migration:
- Proper handling of JDK compiler API packages (com.sun.source.*)
- Manifest includes Add-Exports for Java 9+ module system
- When compiling with JDK 9+, the build automatically adds necessary exports

To check Java version information:
```bash
./gradlew javaVersionInfo
```

To build targeting Java 11 (experimental):
```bash
./gradlew clean buildJava11
```

### For Developers

The Gradle wrapper files (`gradlew`, `gradlew.bat`, `gradle/`) are committed to the repository, so no Gradle installation is required. The wrapper handles:
- Downloading the correct Gradle version (8.5)
- Managing dependencies from Maven Central
- Handling Java 8 compilation with JDK 17
- Preparing for future Java 11+ migration

---

# Design of Export Command
## Concept
Some properties are static while others should be computed via .xml build files. Defects4J uses ant to do this but however there are some redundant steps could be skipped to boost the performance.

This implementation creates simplified build files to accelerate this process and provide backward compatibility. It could be faster if we fully replace the ant backend (e.g. write a build file parser to mock the behaviour of ant to avoid start a jvm) but using simplified build file is fast enough and most cases could be covered by the properties cache.

## Performance
This implementation is perfromance oriented because I think the original defects4j is slow in execution in daily use

### Performance of original defects4j
* checkout and compile all bugs: 42 min
* export all properties: 25 min

## Properties
### cp.compile
```
<target name="export.cp.compile"
            description="Classpath to compile the project"
            depends="sanity.check,compile">
        <fail message="Property file.export not set!" unless="file.export" />

        <path id="project.classpath">
            <pathelement path="${classes.dir}" />
            <path refid="compile.classpath" />
        </path>

        <pathconvert property="cp.compile" refid="project.classpath" />
	<echo message="${cp.compile}" file="${file.export}"/>
</target>
```

It would call target `compile` that is not always requried for only getting a property.
So it could be implemented using a special c4j.before-get-cp property which could be customed in
the project's build file.

### tests.all
Some projects required to search .class files because there may be embedded classes 
but compilation seems to be not required. We can add a property to allow special search logic.
