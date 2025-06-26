package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;
import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.Project;

public class AppendProperty extends Task {
    private String propertyName;
    private String value;
    private String sep;

    public void setPropertyName(String propertyName) {
        this.propertyName = propertyName;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public void setSep(String sep) {
        this.sep = sep;
    }

    @Override
    public void execute() throws BuildException {
        if (propertyName == null || value == null) {
            throw new BuildException("Both 'propertyName' and 'value' attributes are required.");
        }
        if(sep == null)
            sep = ":";

        Project project = getProject();
        String original = project.getProperty(propertyName);
        if(original == null)
            project.setProperty(propertyName,  value);
        else
            project.setProperty(propertyName,  original + sep + value);
    }
}
