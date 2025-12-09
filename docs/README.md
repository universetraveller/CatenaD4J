# CatenaD4J Documentation

Welcome to the CatenaD4J documentation! This directory contains comprehensive guides for using CatenaD4J and its APIs.

## Documentation Overview

### For Users

**[Usage Guide](USAGE.md)** - Start here if you want to use CatenaD4J from the command line.

This guide covers:
- Installation and setup
- Complete command reference (checkout, export, reset, etc.)
- Common workflows and examples
- Troubleshooting tips
- Performance optimization

Perfect for: Researchers, students, and practitioners using CatenaD4J for bug repair experiments.

### For Developers

**[Python API Documentation](API.md)** - Reference for programmatic access using Python.

This guide covers:
- Core modules and their functions
- Command implementations (checkout, export, xids)
- Loader system and project-specific customization
- Utility functions for file I/O, caching, and git operations
- Complete examples for batch processing and automation

Perfect for: Developers building tools on top of CatenaD4J, creating custom workflows, or extending the dataset.

**[Java Toolkit API Documentation](JAVA_API.md)** - Reference for the Java components.

This guide covers:
- Defects4J integration classes
- JUnit agent for test instrumentation
- Test execution utilities (JUnit 3 and JUnit 4)
- Custom Ant tasks
- ClassLoader isolation and utility classes
- Building and integrating the toolkit

Perfect for: Developers working with test execution, creating custom test runners, or integrating with build systems.

## Quick Start

### 1. I want to check out and analyze bugs

```bash
# See available projects
catena4j pids

# Check out a specific bug
catena4j checkout -p Chart -v 15b1 -w ./my_bug

# Export properties
catena4j export -p tests.trigger -w ./my_bug
catena4j export -p classes.modified -w ./my_bug
```

→ See [Usage Guide](USAGE.md#common-workflows) for complete workflows.

### 2. I want to automate bug analysis in Python

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import checkout, export
from argparse import Namespace

context = ExecutionContext()
context.args = Namespace(p='Chart', v='15b1', w='./bug', full_history=False)
checkout.run(context)

context.args = Namespace(p='tests.trigger', w='./bug', o=None, 
                        from_cache=False, update_cache=False)
result = export.run(context)
print(result)
```

→ See [Python API Documentation](API.md#examples) for more examples.

### 3. I want to run tests programmatically in Java

```java
import io.github.universetraveller.util.JUnit4Helper;
import org.junit.runner.Result;
import java.util.*;

Map<String, List<String>> tests = new HashMap<>();
tests.put("com.example.MyTest", Arrays.asList("testMethod1"));

Result result = JUnit4Helper.run(tests);
System.out.println(JUnit4Helper.getSummary(result));
```

→ See [Java API Documentation](JAVA_API.md#examples) for more examples.

## Documentation Structure

```
docs/
├── README.md           # This file - documentation index
├── USAGE.md           # Command-line usage guide (~490 lines)
├── API.md             # Python API reference (~755 lines)
└── JAVA_API.md        # Java toolkit API reference (~944 lines)
```

## Key Concepts

Before diving into the documentation, familiarize yourself with these concepts:

- **Catena Bug**: An indivisible bug consisting of multiple code hunks that must all be fixed together
- **Bug ID (bid)**: The original bug identifier from Defects4J
- **Catena ID (cid)**: Unique identifier for bugs generated from the same source bug
- **Version ID**: Format `<bid><b/f><cid>` where b/f indicates buggy or fixed version
- **Loader**: Component responsible for project-specific bug handling
- **Working Directory**: Directory where a bug is checked out

## Common Tasks

### Command Line Tasks

| Task | Command | Documentation |
|------|---------|---------------|
| List projects | `catena4j pids` | [USAGE.md#pids](USAGE.md#pids) |
| List bugs | `catena4j bids -p Chart` | [USAGE.md#bids](USAGE.md#bids) |
| Check out bug | `catena4j checkout -p Chart -v 15b1 -w ./bug` | [USAGE.md#checkout](USAGE.md#checkout) |
| Export property | `catena4j export -p tests.trigger -w ./bug` | [USAGE.md#export](USAGE.md#export) |
| Reset changes | `catena4j reset -w ./bug` | [USAGE.md#reset](USAGE.md#reset) |

### Python API Tasks

| Task | Module | Documentation |
|------|--------|---------------|
| Checkout bug | `catena4j.commands.checkout` | [API.md#checkout](API.md#catena4jcommandscheckout) |
| Export properties | `catena4j.commands.export` | [API.md#export](API.md#catena4jcommandsexport) |
| List IDs | `catena4j.commands.xids` | [API.md#xids](API.md#catena4jcommandsxids) |
| File operations | `catena4j.util` | [API.md#utilities](API.md#catena4jutil) |
| Custom loaders | `catena4j.loaders` | [API.md#loaders](API.md#loaders-api) |

### Java Toolkit Tasks

| Task | Class | Documentation |
|------|-------|---------------|
| Run JUnit 4 tests | `JUnit4Helper` | [JAVA_API.md#junit4helper](JAVA_API.md#class-junit4helper) |
| Run JUnit 3 tests | `JUnit3Helper` | [JAVA_API.md#junit3helper](JAVA_API.md#class-junit3helper) |
| Isolate classloaders | `IsolatedClassLoader` | [JAVA_API.md#isolatedclassloader](JAVA_API.md#class-isolatedclassloader) |
| Instrument tests | `JUnitAgent` | [JAVA_API.md#junitagent](JAVA_API.md#class-junitagent) |
| Export properties | `Defects4JExport` | [JAVA_API.md#defects4jexport](JAVA_API.md#class-defects4jexport) |

## Additional Resources

- **[Main README](../README.md)** - Project overview, installation, and dataset description
- **[Scripts Documentation](../scripts/README.md)** - Experimental reproduction and research scripts
- **[Toolkit README](../toolkit/README.md)** - Java toolkit-specific information
- **[GitHub Repository](https://github.com/universetraveller/CatenaD4J)** - Source code and issue tracker

## Getting Help

If you can't find what you're looking for in these documents:

1. **Check the FAQs** in the [troubleshooting section](USAGE.md#troubleshooting)
2. **Search the documentation** using your browser's search function (Ctrl+F / Cmd+F)
3. **Review the examples** in each documentation file
4. **Open an issue** on the [GitHub repository](https://github.com/universetraveller/CatenaD4J/issues)

## Contributing to Documentation

Found an error or want to improve the documentation? Contributions are welcome!

1. Fork the repository
2. Make your changes to the documentation files in `docs/`
3. Submit a pull request with a clear description of your improvements

## Document Conventions

Throughout the documentation:

- **Code blocks** show exact commands or code to use
- `inline code` represents variable names, file paths, or commands
- **Bold** highlights important concepts or warnings
- > Blockquotes provide additional tips or notes
- Tables summarize options and parameters

## Version Information

This documentation is for CatenaD4J as of December 2024. For the latest updates, check the [main repository](https://github.com/universetraveller/CatenaD4J).

---

**Quick Links:**
[Usage Guide](USAGE.md) | [Python API](API.md) | [Java API](JAVA_API.md) | [Main README](../README.md)
