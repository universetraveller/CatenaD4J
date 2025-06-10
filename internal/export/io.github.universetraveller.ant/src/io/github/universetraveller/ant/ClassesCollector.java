package io.github.universetraveller.ant;

import java.io.File;
import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.regex.Pattern;

import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;

public class ClassesCollector {
    public static List<String> getClasses(String[] sourceFiles, String srcPrefix, Pattern pattern) {
        List<String> results = new ArrayList<>();

        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);

        List<File> fileIntances = new ArrayList<>();
        for(String file : sourceFiles)
            fileIntances.add(new File(srcPrefix, file));

        Iterable<? extends JavaFileObject> files = fileManager.getJavaFileObjectsFromFiles(fileIntances);
        JavacTask task = (JavacTask) compiler.getTask(null, fileManager, null, null, null, files);

        try{
            Iterable<? extends CompilationUnitTree> asts = task.parse();
            for (CompilationUnitTree ast : asts) {
                final String prefix = ast.getPackageName().toString() + ".";
                new TreeScanner<Void, String>() {
                    Deque<String> context = new ArrayDeque<>();

                    @Override
                    public Void visitClass(ClassTree classTree, String path) {
                        String className = classTree.getSimpleName().toString();
                        if (className.isEmpty()) return super.visitClass(classTree, path);

                        String fqName = context.isEmpty() ? className : context.peek() + "$" + className;
                        if (pattern.matcher(className).matches())
                            results.add(prefix + fqName);

                        context.push(fqName);
                        super.visitClass(classTree, path);
                        context.pop();
                        return null;
                    }
                }.scan(ast, null);
            }
        } catch(IOException e) {
            throw new RuntimeException(e);
        }
        return results;
    }
}
