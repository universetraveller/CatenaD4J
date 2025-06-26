cd listener
javac -cp :/root/defects4j/major/lib/* NanoTimingListener.java
cd ..
/root/defects4j/major/bin/ant -cp :/root/defects4j/major/lib/*:/root/workbench/CatenaD4J/toolkit/target/toolkit.jar:/root/workbench/CatenaD4J/scripts/tests/test-c4j-export/listener/ -Dbasedir=/tmp/bugs_static/Closure_128 -Dd4j.home=/root/defects4j -Dc4j.d4j.properties=/root/workbench/CatenaD4J/resources/defects4j.properties -Dd4j.workdir=/tmp/bugs_static/Closure_128 -f /root/workbench/CatenaD4J/projects/Closure/Closure.export.xml -listener NanoTimingListener compile
rm listener/NanoTimingListener.class
