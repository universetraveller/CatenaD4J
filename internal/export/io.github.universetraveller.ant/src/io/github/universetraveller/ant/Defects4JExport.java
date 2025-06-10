package io.github.universetraveller.ant;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Vector;
import java.util.regex.Pattern;

import org.apache.tools.ant.Project;
import org.apache.tools.ant.ProjectHelper;
import org.apache.tools.ant.types.FileSet;
import org.apache.tools.ant.types.Path;
import org.apache.tools.ant.helper.ProjectHelper2;

/**
 * Required as system properties:
 *   basedir
 *   d4j.home
 * 
 * Not included properties:
 * 	 d4j.bug.id
 * 	 d4j.dir.src.classes
 * 	 d4j.dir.src.tests
 * 	 d4j.classes.modified
 * 	 d4j.classes.relevant
 * 	 d4j.tests.trigger
 *
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
public class Defects4JExport {

	Project project;

	public Defects4JExport(String file) {
		project = new Project();

		project.init();

		ProjectHelper.configureProject(project, new File(file));
	}

	public Defects4JExport(String[] files) {
		project = new Project();

		project.init();

		ProjectHelper2 helper = new ProjectHelper2();
		project.addReference("ant.projectHelper", helper);

		for(String file : files)
			helper.parse(project, new File(file));
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
		Defects4JExport export = new Defects4JExport(args[0].split(","));

		String result = export.getProperty(args[1]);
		if(result == null)
			throw new RuntimeException(String.format(
											"Could not found property %s",
											args[1]));

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

		Pattern prefix = Pattern.compile(String.format("^(?:%s|%s)",
														Pattern.quote(srcPrefix + sep),
														Pattern.quote(binPrefix + sep)));

		Pattern suffix = Pattern.compile("\\.(?:java|class)$");

		String[] files = paths.getDirectoryScanner().getIncludedFiles();

		String process = project.getProperty("c4j.source-to-classes");
		if(process != null) 
		{}

		for(int i = 0; i < files.length; ++ i)
			files[i] = formatGetTestsAll(files[i], prefix, suffix);

		// how about System.lineSeparator()?
		return String.join(project.getProperty("line.separator"), files)
						.replaceAll(sep, ".");
	}
}
