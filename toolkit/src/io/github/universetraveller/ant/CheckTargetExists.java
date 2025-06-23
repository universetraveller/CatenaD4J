package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;
import org.apache.tools.ant.BuildException;

public class CheckTargetExists extends Task {
    private String targetName;
    private String setProperty;

    public void setTarget(String targetName) {
        this.targetName = targetName;
    }

    public void setSetProperty(String setProperty) {
        this.setProperty = setProperty;
    }

    @Override
    public void execute() throws BuildException {
        if (targetName == null || setProperty == null) {
            throw new BuildException("Both 'target' and 'setProperty' attributes are required.");
        }

        if (getProject().getTargets().containsKey(targetName)) {
            getProject().setNewProperty(setProperty, "true");
        }
    }
}
