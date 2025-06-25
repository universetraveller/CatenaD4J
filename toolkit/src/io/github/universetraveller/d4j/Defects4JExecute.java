package io.github.universetraveller.d4j;

import java.io.IOException;
import java.io.PrintStream;

import org.apache.tools.ant.BuildLogger;
import org.apache.tools.ant.DefaultLogger;
import org.apache.tools.ant.Project;

public class Defects4JExecute extends Defects4JExport {

    public Defects4JExecute(String projectBuildFile) {
        super(projectBuildFile);
    }

    public Defects4JExecute(String[] files) {
        super(files);
    }

    public void execute(String target) {
        project.executeTarget(target);
    }

    public void addLogger(BuildLogger logger) {
        project.addBuildListener(logger);
    }

    public static void main(String[] args) throws IOException {
        Defects4JExecute executor = new Defects4JExecute(args[0]);

        if(args.length > 2) {
            PrintStream out = new PrintStream(args[2]);
            DefaultLogger logger = new DefaultLogger();
            logger.setOutputPrintStream(out);
            logger.setErrorPrintStream(out);
            logger.setMessageOutputLevel(Project.MSG_INFO);
            executor.addLogger(logger);
        }

        executor.execute(args[1]);;
    }
}