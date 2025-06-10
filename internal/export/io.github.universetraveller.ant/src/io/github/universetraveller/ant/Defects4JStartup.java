package io.github.universetraveller.ant;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Properties;

import org.apache.tools.ant.Project;
import org.apache.tools.ant.ProjectHelper;
import org.apache.tools.ant.types.Path;
import org.apache.tools.ant.helper.ProjectHelper2;
import org.apache.tools.ant.taskdefs.Property;
import org.apache.tools.ant.taskdefs.Taskdef;

public class Defects4JStartup {

    Project project;
    ProjectHelper projectHelper;
    final String defects4jBuildProperties = "defects4j.build.properties";

    public Project getProject() {
        return project;
    }

    public ProjectHelper getProjectHelper() {
        return projectHelper;
    }

    public Defects4JStartup() {
        project = new Project();

		project.init();
    }

    public void initializeProjectHelper2() {
		projectHelper = new ProjectHelper2();
		project.addReference("ant.projectHelper", projectHelper);
    }

    public Defects4JStartup(String file) {
        this();

		ProjectHelper.configureProject(project, new File(file));
        projectHelper = (ProjectHelper) project.getReference("ant.projectHelper");
    }

    public Defects4JStartup(String[] files) {
        this();

        initializeProjectHelper2();

		for(String file : files)
			projectHelper.parse(project, new File(file));
    }

    public void initializeLibraries(Properties props) {
        String d4jHome = project.getProperty("d4j.home");
        if(d4jHome == null) 
            throw new RuntimeException("Property d4j.home not set!");

        Taskdef taskdef = new Taskdef();
        taskdef.setProject(project);
        taskdef.setResource(props.getProperty("res.antcontrib.xml"));

        Path cp = new Path(project);
        cp.setPath(d4jHome + props.getProperty("rel.antcontrib.jar"));
        taskdef.setClasspath(cp);

        taskdef.execute();

        project.setProperty("junit.jar", d4jHome + props.getProperty("rel.junit.jar"));
        project.setProperty("cobertura.jar", d4jHome + props.getProperty("rel.cobertura.jar"));
        project.setProperty("cobertura.lib", d4jHome + props.getProperty("rel.cobertura.lib"));
    }

    public void initializeProperties(String basedir) {
        project.setProperty("d4j.workdir", basedir);

        String buildProperties = basedir + "/" + defects4jBuildProperties;
        if(!Files.exists(Paths.get(buildProperties)))
            throw new RuntimeException("Directory " + basedir + " is not a Defects4J working directory!");
        
        Property propertyTask = new Property();
        propertyTask.setProject(project);
        propertyTask.setFile(new File(buildProperties));
        propertyTask.execute();
    }

    public void initializeDefects4J(String propertyFile, String basedir) {
        try {
            project.setBaseDir(new File(basedir));

            Properties props = new Properties();
            props.load(new FileInputStream(propertyFile));

            initializeLibraries(props);

            initializeProperties(basedir);

        } catch (FileNotFoundException e) {
            throw new RuntimeException("Property c4j.d4j.properties is not set");
        } catch (IOException e) {
            throw new RuntimeException("Failed to load defects4j properties");
        }
    }
}
