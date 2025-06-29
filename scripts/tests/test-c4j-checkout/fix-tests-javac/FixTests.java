import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

import com.sun.source.tree.AnnotationTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.LineMap;
import com.sun.source.tree.MethodTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.SourcePositions;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;

public class FixTests {
    public static void main(String[] args) throws Exception {
        long startTime = System.currentTimeMillis();
        Map<String, Set<String>> methods = new HashMap<>();
        Map<String, List<String>> buffers = new HashMap<>();
        int index;
        String fileName;
        for(String arg : args) {
            index = arg.indexOf(':', 0);
            fileName = arg.substring(0, index);

            if(!methods.containsKey(fileName)) {
                methods.put(fileName, new HashSet<>(Arrays.asList(arg.substring(index+1).split(","))));
                buffers.put(fileName, Files.readAllLines(Paths.get(fileName)));
            }
        }
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);

        Iterable<? extends JavaFileObject> files = fileManager.getJavaFileObjectsFromStrings(methods.keySet());
        JavacTask task = (JavacTask) compiler.getTask(null, fileManager, null, null, null, files);

        Iterable<? extends CompilationUnitTree> asts = task.parse();
        //task.analyze();
        Trees trees = Trees.instance(task);
        for (CompilationUnitTree ast : asts) {
            LineMap lineMap = ast.getLineMap();
            String currentFile = ast.getSourceFile().getName();
            if(!methods.containsKey(currentFile))
                continue;
            
            Set<String> toRemove = methods.get(currentFile);
            List<String> lines = buffers.get(currentFile);
            int[] classEnd = new int[3];

            new TreeScanner<Void, Void>() {
                public Void visitImport(com.sun.source.tree.ImportTree node, Void p) {
                    classEnd[2] = node.getQualifiedIdentifier().toString().contains("org.junit.Test") ? 1 : 0;
                    return super.visitImport(node, p);
                };
                @Override
                public Void visitClass(com.sun.source.tree.ClassTree node, Void p) {
                    SourcePositions pos = trees.getSourcePositions();
                    long end = pos.getEndPosition(ast, node);
                    classEnd[0] = (int) lineMap.getLineNumber(end);
                    classEnd[1] = (int) lineMap.getColumnNumber(end);
                    return super.visitClass(node, p);
                };
                @Override
                public Void visitMethod(MethodTree methodTree, Void unused) {
                    String name = methodTree.getName().toString();
                    if(toRemove.contains(name)) {
                        SourcePositions pos = trees.getSourcePositions();
                        long start = pos.getStartPosition(ast, methodTree);
                        int startLine = (int) lineMap.getLineNumber(start);
                        long end = pos.getEndPosition(ast, methodTree);
                        int endLine = (int) lineMap.getLineNumber(end);
                        for(int i = startLine - 1; i < endLine; ++i) {
                            lines.set(i, "// " + lines.get(i));
                        }
                        lines.set(startLine - 1, "public void " + name + "()\n// Defects4J: flaky method\n" + lines.get(startLine - 1));
                        for (AnnotationTree annotation : methodTree.getModifiers().getAnnotations()) {
                            if(annotation.getAnnotationType().toString().equals("Test")) {
                                lines.set(startLine - 1, "@Test\n" + lines.get(startLine - 1));
                                break;
                            }
                        }
                        toRemove.remove(name);
                    }
                    return super.visitMethod(methodTree, unused);
                }
            }.scan(ast, null);
            if(!toRemove.isEmpty()) {
                for(String met : toRemove) {
                    String line = lines.get(classEnd[0] - 1);
                    if(classEnd[2] == 1)
                        line = line.substring(0, classEnd[1] - 2) + "    @Test\n    public void " + met + "() {} // Fails in super class\n" + line.substring(classEnd[1] -1);
                    else
                        line = line.substring(0, classEnd[1] - 2) + "    public void " + met + "() {} // Fails in super class\n" + line.substring(classEnd[1] -1);
                    lines.set(classEnd[0] - 1, line);
                }
            }
            Path backup = Paths.get(currentFile + ".bak");
            Path f = Paths.get(currentFile);
            Files.copy(f, backup, StandardCopyOption.REPLACE_EXISTING);
            Files.write(f, lines);
        }
        long endTime = System.currentTimeMillis();
        System.out.println(String.valueOf(endTime - startTime) + " ms");
    }
}

