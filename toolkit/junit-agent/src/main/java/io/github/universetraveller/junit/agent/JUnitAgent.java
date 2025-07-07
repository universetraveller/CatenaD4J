package io.github.universetraveller.junit.agent;

import java.lang.instrument.Instrumentation;
import java.util.List;
//import java.io.File;

public class JUnitAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        //try {
        //   // Needed if JUnit is in the bootstrap classloader
        //   File agentJar = new
        //   File(MyAgent.class.getProtectionDomain().getCodeSource().getLocation().toURI());
        //   inst.appendToBootstrapClassLoaderSearch(new java.util.jar.JarFile(agentJar));
        //} catch (Exception e) {
        //   e.printStackTrace();
        //}

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            List<JUnitRecorder.FailureRecord> failures = JUnitRecorder.getFailures();
            if (!failures.isEmpty()) {
                System.out.println("\n=== Intercepted Assert.fail(String) Calls ===");
                for (JUnitRecorder.FailureRecord record : failures) {
                    System.out.println("fail(\"" + record.message + "\")");
                    System.out.println("Caused by:");
                    for (String frame : record.userStack) {
                        System.out.print("  ");
                        System.out.println(frame);
                    }
                    System.out.println("---");
                }
                System.out.println("\n=== Length: " + failures.size() + " ===");
            }
        }));
        JUnitTransformer.install(inst);
    }
}
