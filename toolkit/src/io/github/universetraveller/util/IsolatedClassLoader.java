package io.github.universetraveller.util;

import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;
import java.util.List;

public class IsolatedClassLoader extends URLClassLoader {
    // Lang's tests org.apache.commons.lang.enums.ValuedEnumTest#testCompareTo_classloader_equal
    // and org.apache.commons.lang.enums.ValuedEnumTest#testCompareTo_classloader_different
    // check if the class loader is a URLClassLoader which leads to unexpected failing tests
    // while ant doesn't even execute it because ant uses AntClassLoader which directly inherited
    // from ClassLoader
    List<String> systemPackages = new ArrayList<>();
    boolean fallBackToParent;
    boolean allowChildToFindSystemClass;

    public IsolatedClassLoader(URL[] urls, ClassLoader parent, boolean fallBackToParent, boolean allowChildToFindSystemClass) {
        super(urls, parent);
        this.fallBackToParent = fallBackToParent;
        this.allowChildToFindSystemClass = allowChildToFindSystemClass;
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
        // Child-first: try to find class from this classloader first
        synchronized (getClassLoadingLock(name)) {
            // Check if class is already loaded
            Class<?> c = findLoadedClass(name);
            if (c != null) {
                return c;
            }

            // Delegate system packages to parent immediately
            if(isInSystemPackages(name)) {
                try {
                    c = super.loadClass(name, resolve);
                } catch (ClassNotFoundException e) {
                    if(!allowChildToFindSystemClass)
                        throw new ClassNotFoundException("Class not found in parent classloader: " + name, e);

                    c = findClass(name);
                }
            } else {
                try {
                    c = findClass(name);
                } catch (ClassNotFoundException e) {
                    if(!fallBackToParent)
                        throw new ClassNotFoundException("Class not found in isolated classloader: " + name, e);
                    
                    // ensure the class is tried to load
                    c = super.loadClass(name, resolve);
                }
            }

            if (resolve) {
                resolveClass(c);
            }

            return c;
        }
    }

    public IsolatedClassLoader copy() {
        IsolatedClassLoader loader = new IsolatedClassLoader(getURLs(), getParent(), fallBackToParent, allowChildToFindSystemClass);
        loader.systemPackages = this.systemPackages;
        return loader;
    }
}
