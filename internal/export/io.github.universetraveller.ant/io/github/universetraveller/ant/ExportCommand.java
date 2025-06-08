package io.github.universetraveller.ant;

/**
 * Required as input values:
 * 	basedir
 *      d4j.home
 *      d4j.project.id
 *      
 * Not included properties:
 *	d4j.bug.id
 *	d4j.dir.src.classes
 *	d4j.dir.src.tests
 *	d4j.classes.modified
 *	d4j.classes.relevant
 *	d4j.tests.trigger
 *
 * Static properties:
 * 	classes.modified
 *      classes.relevant
 *      dir.src.classes
 *      dir.src.tests
 *      tests.trigger
 *
 * Dynamic properties:
 * 	cp.compile
 * 	cp.test
 * 	dir.bin.classes
 * 	dir.bin.tests
 * 	tests.all
 * 	tests.relevant
 **/
public class ExportCommand {

	public static void main(String[] args) {
	}

	public List<String> getProperty() {
	}
}
