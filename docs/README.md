# CatenaD4J API Documentation

This directory contains comprehensive API documentation for CatenaD4J's Python and Java components.

## Python API

The Python API provides programmatic access to CatenaD4J's core functionality.

### Core Components

- **[Commands](python/commands.md)** - checkout, export, and ID query commands
- **[Loaders](python/loaders.md)** - Project-specific bug loading system
- **[Utilities](python/utilities.md)** - File I/O, git operations, caching, and helpers

### Quick Example

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import checkout, export
from argparse import Namespace

# Initialize context
context = ExecutionContext()

# Check out a bug
context.args = Namespace(p='Chart', v='15b1', w='./bug', full_history=False)
checkout.run(context)

# Export properties
context.args = Namespace(p='tests.trigger', w='./bug', o=None,
                        from_cache=False, update_cache=False)
result = export.run(context)
```

## Java Toolkit API

The Java toolkit provides test execution, instrumentation, and build integration.

### Core Components

- **[Test Runners](java/test-runners.md)** - JUnit 3 and 4 test execution with isolation
- **[JUnit Agent](java/junit-agent.md)** - Bytecode instrumentation for test interception
- **[Ant Tasks](java/ant-tasks.md)** - Custom Ant tasks for build automation
- **[Defects4J Integration](java/defects4j.md)** - Property export and integration classes

### Quick Example

```java
import io.github.universetraveller.util.JUnit4Helper;
import org.junit.runner.Result;
import java.util.*;

Map<String, List<String>> tests = new HashMap<>();
tests.put("com.example.MyTest", Arrays.asList("testMethod1", "testMethod2"));

Result result = JUnit4Helper.run(tests);
System.out.println(JUnit4Helper.getSummary(result));
```

## Getting Started

### For Python Developers

1. Read the [Commands documentation](python/commands.md) to understand available operations
2. Check [Loaders](python/loaders.md) for project-specific customization
3. Use [Utilities](python/utilities.md) for helper functions

### For Java Developers

1. Start with [Test Runners](java/test-runners.md) for test execution
2. See [JUnit Agent](java/junit-agent.md) for test instrumentation
3. Review [Defects4J Integration](java/defects4j.md) for property export

## API Structure

```
docs/
├── README.md              # This file
├── python/
│   ├── commands.md        # Command implementations
│   ├── loaders.md         # Project loaders and customization
│   └── utilities.md       # Helper functions and utilities
└── java/
    ├── test-runners.md    # JUnit test execution
    ├── junit-agent.md     # Bytecode instrumentation
    ├── ant-tasks.md       # Build system integration
    └── defects4j.md       # Defects4J integration
```

## Common Tasks

### Python API Tasks

| Task | Module | Documentation |
|------|--------|---------------|
| Checkout bug | `catena4j.commands.checkout` | [Commands](python/commands.md#checkout) |
| Export properties | `catena4j.commands.export` | [Commands](python/commands.md#export) |
| List IDs | `catena4j.commands.xids` | [Commands](python/commands.md#xids) |
| Custom loader | `catena4j.loaders.project_loader` | [Loaders](python/loaders.md) |
| File operations | `catena4j.util` | [Utilities](python/utilities.md#file-operations) |
| Git operations | `catena4j.c4jutil` | [Utilities](python/utilities.md#git-operations) |

### Java API Tasks

| Task | Class | Documentation |
|------|-------|---------------|
| Run JUnit 4 tests | `JUnit4Helper` | [Test Runners](java/test-runners.md#junit4helper) |
| Run JUnit 3 tests | `JUnit3Helper` | [Test Runners](java/test-runners.md#junit3helper) |
| Intercept failures | `JUnitAgent` | [JUnit Agent](java/junit-agent.md) |
| Isolate classloaders | `IsolatedClassLoader` | [Test Runners](java/test-runners.md#isolatedclassloader) |
| Export properties | `Defects4JExport` | [Defects4J](java/defects4j.md#defects4jexport) |
| Custom Ant task | `AppendProperty`, etc. | [Ant Tasks](java/ant-tasks.md) |

## Additional Resources

- **[Main README](../README.md)** - Command-line usage and overview
- **[Scripts Documentation](../scripts/README.md)** - Experiment reproduction
- **[GitHub Repository](https://github.com/universetraveller/CatenaD4J)** - Source code

## Contributing

To contribute to the API:

1. Follow existing code patterns and conventions
2. Add documentation for new public APIs
3. Include examples for complex functionality
4. Update this index when adding new modules

## Support

- **Issues:** [GitHub Issues](https://github.com/universetraveller/CatenaD4J/issues)
- **Discussions:** Use GitHub Discussions for questions
- **Email:** See repository for contact information
