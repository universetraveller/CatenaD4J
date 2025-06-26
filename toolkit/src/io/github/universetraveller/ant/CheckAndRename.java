package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;
import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.Project;
import org.apache.tools.ant.Target;

public class CheckAndRename extends Task {
    
    private String targetName;
    private String setProperty;
    private String newName;

    public void setNewName(String newName) {
        this.newName = newName;
    }

    public void setTarget(String targetName) {
        this.targetName = targetName;
    }

    public void setSetProperty(String setProperty) {
        this.setProperty = setProperty;
    }

    @Override
    public void execute() throws BuildException {
        if (targetName == null || setProperty == null || newName == null) {
            throw new BuildException("All 'target', 'newName' and 'setProperty' attributes are required.");
        }

        Project project = getProject();
        if (project.getTargets().containsKey(targetName)) {
            Target newTarget = new Target();
            newTarget.addDependency(targetName);
            newTarget.setName(newName);
            project.addTarget(newTarget);
            project.setNewProperty(setProperty, "true");
        }
    }
}
