package io.github.universetraveller.junit.agent;

import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;

import net.bytebuddy.agent.builder.AgentBuilder;
import net.bytebuddy.matcher.ElementMatchers;
import net.bytebuddy.utility.JavaModule;
import net.bytebuddy.description.type.TypeDescription;
import net.bytebuddy.dynamic.DynamicType;

import static net.bytebuddy.matcher.ElementMatchers.*;

public class JUnitTransformer {
    public static void install(Instrumentation inst) {
        new AgentBuilder.Default()
            .ignore(ElementMatchers.none())
            .type(nameStartsWith("junit.framework.Assert").or(nameStartsWith("org.junit.Assert")))
            .transform(new AgentBuilder.Transformer() {
                @Override
                public DynamicType.Builder<?> transform(
                        DynamicType.Builder<?> builder,
                        TypeDescription typeDescription,
                        ClassLoader classLoader,
                        JavaModule module,
                        ProtectionDomain protectionDomain) {

                    return builder.method(named("fail").and(takesArguments(String.class)))
                            .intercept(net.bytebuddy.implementation.MethodDelegation.to(JUnitInterceptor.class));
                }
            })
            .installOn(inst);
    }
}

