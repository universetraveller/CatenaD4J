package io.github.universetraveller.util;

import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;
import java.util.List;

public class IsolatedClassLoader extends URLClassLoader {
    List<String> systemPackages = new ArrayList<>();

    public IsolatedClassLoader(URL[] urls, ClassLoader parent) {
        super(urls, parent);
    }

    public void addSystemPackageRoot(String prefix) {
        if(prefix.endsWith("."))
            systemPackages.add(prefix);
        else
            systemPackages.add(prefix + ".");
    }

    public void addJREPackages() {
        addSystemPackageRoot("java.");
        addSystemPackageRoot("javax.");
        addSystemPackageRoot("jdk.");
        addSystemPackageRoot("com.sun.java.");
        addSystemPackageRoot("com.sun.org.apache.");
        addSystemPackageRoot("com.sun.jndi.");
        addSystemPackageRoot("com.sun.rmi.");
        addSystemPackageRoot("com.sun.corba.");
        addSystemPackageRoot("com.sun.naming.");
        addSystemPackageRoot("com.sun.image.");
        addSystemPackageRoot("com.sun.media.");
        addSystemPackageRoot("com.sun.org.omg.");
        addSystemPackageRoot("sun.");
        addSystemPackageRoot("sunw.");
        addSystemPackageRoot("org.xml.sax.");
        addSystemPackageRoot("org.w3c.dom.");
        addSystemPackageRoot("org.ietf.jgss.");
        addSystemPackageRoot("org.omg.");
    }

    public boolean isInSystemPackages(String name) {
        return systemPackages.stream().anyMatch(name::startsWith);
    }

    public boolean isInThisLoader(String name) {
        return findResource(name.replace(".", "/") + ".class") != null;
    }

    @Override
    public Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
        // Delegate system packages to parent immediately
        if (isInSystemPackages(name)) {
            return super.loadClass(name, resolve);
        }

        // Child-first: try to find class from this classloader first
        synchronized (getClassLoadingLock(name)) {
            // Check if class is already loaded
            Class<?> c = findLoadedClass(name);
            if (c == null) {
                try {
                    c = findClass(name);
                } catch (ClassNotFoundException e) {
                    //c = super.loadClass(name, resolve);
                    throw new ClassNotFoundException("Class not found in isolated classloader: " + name, e);
                }
            }
            if (resolve) {
                resolveClass(c);
            }
            return c;
        }
    }
}
