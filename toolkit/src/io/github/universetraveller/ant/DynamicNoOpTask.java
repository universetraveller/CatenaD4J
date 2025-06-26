package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;
import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.DynamicAttribute;
import org.apache.tools.ant.DynamicElement;

public class DynamicNoOpTask extends Task implements DynamicAttribute, DynamicElement {
    @Override
    public void setDynamicAttribute(String name, String value) throws BuildException {
    }

    @Override
    public Object createDynamicElement(String name) throws BuildException {
        return new DummyElement(name);
    }

    @Override
    public void execute() throws BuildException {
        return;
    }
}

class DummyElement implements DynamicAttribute, DynamicElement {
    private final String name;

    public DummyElement(String name) {
        this.name = name;
    }

    @Override
    public void setDynamicAttribute(String attrName, String value) {
        // Ignore
    }

    @Override
    public Object createDynamicElement(String subElementName) {
        return new DummyElement(name + "/" + subElementName);
    }
}