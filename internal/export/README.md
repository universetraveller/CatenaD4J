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
So it could be implemented using a special c4j.pre-get-cp property which could be customed in
the project's build file.

### tests.all
Some projects required to search .class files because there may be embedded classes 
but compilation seems to be not required. We can add a c4j.tests-filter 
property to allow special search logic.
