if [ ! -d "./target" ]; then
	mkdir target
fi
javac -cp :/root/defects4j/major/lib/* -sourcepath ./src -d ./target src/io/github/universetraveller/ant/Defects4JExport.java
jar cf ./target/Export.jar -C ./target .
