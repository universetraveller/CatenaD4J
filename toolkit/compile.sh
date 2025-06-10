if [ ! -d "./target" ]; then
	mkdir target
fi
javac -cp :${1:-/root/defects4j}/major/lib/* -sourcepath ./src -d ./target src/io/github/universetraveller/d4j/*.java src/io/github/universetraveller/util/*.java
jar cf ${2:-./target/}toolkit.jar -C ./target .
