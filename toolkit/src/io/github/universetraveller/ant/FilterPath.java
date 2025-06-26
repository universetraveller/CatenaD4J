package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Pattern;

import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.Project;
import org.apache.tools.ant.types.Path;

public class FilterPath extends Task {
    private Pattern include;
    private Pattern exclude;
    private String pathString;
    private String sep;
    private String targetPath;

    public void setSep(String sep) {
        this.sep = sep;
    }

    public void setTargetPath(String tp) {
        this.targetPath = tp;
    }

    public void setPathString(String ps) {
        this.pathString = ps;
    }

    public void setInclude(String inc) {
        this.include = Pattern.compile(inc);
    }

    public void setExclude(String exc) {
        this.exclude = Pattern.compile(exc);
    }

    @Override
    public void execute() throws BuildException {
        if (pathString == null) {
            throw new BuildException("All 'include', 'exclude' and 'pathString' attributes are required.");
        }

        if(sep == null)
            sep = ":";

        List<String> included = new ArrayList<>();
        for(String p : pathString.split(sep)) {
            if(exclude != null && exclude.matcher(p).matches())
                continue;
            if(include != null && !include.matcher(p).matches())
                continue;
            included.add(p);
        }
        Collections.sort(included);
        Project project = getProject();
        Path finalPath = new Path(project);
        finalPath.setPath(String.join(sep, included));
        project.addReference(targetPath, finalPath);
    }
}
