# Design of Export Command
## Concept
Some properties are static while others should be computed via .xml build files. Defects4J uses ant to do this but however there are some redundant steps could be skipped to boost the performance.

This implementation creates simplified build files to accelerate this process and provide backward compatibility. It could be faster if we fully replace the ant backend (e.g. write a build file parser to mock the behaviour of ant to avoid start a jvm) but using simplified build file is fast enough and most cases could be covered by the properties cache.
