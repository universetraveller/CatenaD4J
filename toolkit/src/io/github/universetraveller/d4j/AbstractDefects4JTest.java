package io.github.universetraveller.d4j;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/*
 * The target is to create a minimal test runner
 * some useful features like orderer, abort on failure, verify patches
 * that are not very important to a dataset are not added currently
 */
public abstract class AbstractDefects4JTest extends Defects4JExport {
    Map<String, List<String>> methods;

    public AbstractDefects4JTest(String projectBuildFile) throws MalformedURLException {
        super(projectBuildFile);
    }

    abstract public void run() throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, IOException, Exception;

    public void addTest(String classOrTest) {
        int idx = classOrTest.indexOf('#');
        String className = idx < 0 ? classOrTest : classOrTest.substring(0, idx);
        methods.putIfAbsent(className, null);
        if(idx > 0) {
            if(methods.get(className) == null) {
                methods.put(className, new ArrayList<>());
            }
            methods.get(className).add(classOrTest.substring(idx + 1));
        }
    }

    public static AbstractDefects4JTest getRunner(String identifier, String configuration) throws MalformedURLException {
        if(identifier == null) {
            return new Defects4JTest(configuration);
        } else if(identifier.equals("ant")) {
            return new Defects4JTest1(configuration);
        } else {
            throw new MalformedURLException("Unknown runner identifier " + identifier);
        }
    }

    public static void main(String[] args) throws IOException {
        AbstractDefects4JTest runner = getRunner(System.getProperty("c4j.test.runner"), args[0]);

        for(int i = 1; i < args.length; ++ i)
            runner.addTest(args[i]);
        
        try {
            runner.run();
            System.exit(0);
        } catch (ClassNotFoundException | NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
            throw new IOException(e);
        } catch (Exception e) {
            throw new IOException(e);
        }
    }
}