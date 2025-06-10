package io.github.universetraveller.d4j;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Vector;
import java.util.regex.Pattern;

import org.apache.tools.ant.types.FileSet;
import org.apache.tools.ant.types.Path;

import io.github.universetraveller.util.ClassesCollector;

/**
 * Static properties:
 *   classes.modified
 *   classes.relevant
 *   dir.src.classes
 *   dir.src.tests
 *   tests.trigger
 *   tests.relevant
 *
 * Dynamic properties:
 *   cp.compile
 *   cp.test
 *   dir.bin.classes
 *   dir.bin.tests
 *   tests.all
 **/
public class Defects4JExport extends Defects4JStartup {

	public Defects4JExport(String projectBuildFile) {
		super();

		initializeProjectHelper2();

		initializeDefects4J(System.getProperty("c4j.d4j.properties"),
							System.getProperty("basedir"));

		projectHelper.parse(project, new File(projectBuildFile));
	}

	public Defects4JExport(String[] files) {
		super(files);
	}

	public String getProperty(String property) {
		switch (property) {
			case "cp.compile":
				return getCompileClasspath();
		
			case "cp.test":
				return getTestClasspath();

			case "dir.bin.classes":
				return getDirBinClasses();

			case "dir.bin.tests":
				return getDirBinTests();

			case "tests.all":
				return getTestsAll();

			default:
				return project.getProperty(property);
		}
	}

	public static void main(String[] args) throws IOException {
		Defects4JExport export = new Defects4JExport(args[0]);

		String result = export.getProperty(args[1]);
		if(result == null)
			throw new RuntimeException("Could not found property " + args[1]);

		PrintStream out = args.length > 2 ?
							new PrintStream(args[2]) :
							System.out;

		out.print(result);
		out.flush();
		out.close();
	}

	private void beforeGetClasspath() {
		String targets = project.getProperty("c4j.before-get-cp");

		if(targets != null)
			project.executeTargets(new Vector<String>(Arrays.asList(targets.split(","))));
	}

	public String getCompileClasspath() {
		beforeGetClasspath();

		Path cp = new Path(project);
		cp.setPath(project.getProperty("classes.dir"));
		cp.add((Path) project.getReference("compile.classpath"));

		return cp.toString();
	}

	public String getTestClasspath() {
		beforeGetClasspath();
		return project.getReference("d4j.test.classpath").toString();
	}

	public String getRelDirBin(String property) {
		return project.getBaseDir()
						.toPath()
						.relativize(
							Paths.get(project.getProperty(property))
						).toString();
	}

	public String getDirBinClasses() {
		return getRelDirBin("classes.dir");
	}

	public String getDirBinTests() {
		return getRelDirBin("test.classes.dir");
	}

	private static String formatGetTestsAll(String path, Pattern prefix, Pattern suffix) {
		path = prefix.matcher(path).replaceFirst("");
		return suffix.matcher(path).replaceFirst("");
	}

	public String getTestsAll() {
		FileSet paths = (FileSet) project.getReference("all.manual.tests");

		String srcPrefix = Paths.get(project.getBaseDir().getAbsolutePath(),
										project.getProperty("d4j.dir.src.tests"))
								.toString();

		String binPrefix = project.getProperty("test.home");

		// how about File.pathSeparator?
		String sep = project.getProperty("file.separator");

		Pattern prefix = Pattern.compile(new StringBuilder()
												.append("^(?:")
												.append(Pattern.quote(srcPrefix + sep))
												.append("|")
												.append(Pattern.quote(binPrefix + sep))
												.append(")")
												.toString());

		Pattern suffix = Pattern.compile("\\.(?:java|class)$");

		String[] files = paths.getDirectoryScanner().getIncludedFiles();

		String process = project.getProperty("c4j.tests.getter.predict");
		if(process != null) 
			return String.join(project.getProperty("line.separator"), ClassesCollector.getClasses(files, srcPrefix, Pattern.compile(process)));

		for(int i = 0; i < files.length; ++ i)
			files[i] = formatGetTestsAll(files[i], prefix, suffix);

		// how about System.lineSeparator()?
		return String.join(project.getProperty("line.separator"), files)
						.replaceAll(sep, ".");
	}
}
