# CatenaD4J Architecture Overview

## Table of Contents
- [Introduction](#introduction)
- [System Architecture](#system-architecture)
- [Component Overview](#component-overview)
- [Bootstrap Process](#bootstrap-process)
- [Python-Java Integration](#python-java-integration)
- [Command Execution Flow](#command-execution-flow)
- [Data Flow](#data-flow)
- [Extension Architecture](#extension-architecture)
- [Performance Considerations](#performance-considerations)

## Introduction

CatenaD4J is designed as a modular, extensible dataset infrastructure with a Python frontend and Java performance backend. The architecture emphasizes:

- **Modularity**: Components are loosely coupled and independently replaceable
- **Extensibility**: Custom commands and loaders can be added without modifying core code
- **Performance**: Java toolkit handles computationally intensive operations
- **Compatibility**: Works as a Defects4J plugin while maintaining independent functionality

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (CLI / Python API)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Bootstrap System                           │
│  • System Initialization   • Configuration Loading           │
│  • Component Registration  • Entry Point Management          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌─────▼──────┐ ┌──────▼───────┐
│   Commands    │ │  Loaders   │ │  Utilities   │
│               │ │            │ │              │
│ • checkout    │ │ • Project  │ │ • File I/O   │
│ • export      │ │   Loaders  │ │ • VCS Ops    │
│ • test        │ │ • Default  │ │ • Cache      │
│ • compile     │ │   Loader   │ │ • Properties │
└───────┬───────┘ └─────┬──────┘ └──────┬───────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │                               │
┌───────▼────────┐         ┌───────────▼──────────┐
│  Defects4J     │         │   Java Toolkit       │
│  Integration   │         │                      │
│                │         │  • Ant Tasks         │
│ • Metadata     │◄────────┤  • Export Engine     │
│ • Repository   │         │  • Test Runner       │
│ • Properties   │         │  • Utilities         │
└────────────────┘         └──────────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Build Systems      │
                          │  • Ant              │
                          │  • Maven            │
                          │  • Gradle           │
                          └─────────────────────┘
```

### Directory Structure

```
CatenaD4J/
├── catena4j/                    # Python source code
│   ├── __init__.py
│   ├── _bootstrap.py            # Low-level bootstrap APIs
│   ├── bootstrap.py             # High-level initialization
│   ├── config.py                # System configuration
│   ├── env.py                   # Environment management
│   ├── dispatcher.py            # Command dispatcher
│   ├── exceptions.py            # Custom exceptions
│   ├── c4jutil.py              # CatenaD4J utilities
│   ├── d4jutil.py              # Defects4J integration
│   ├── util.py                 # General utilities
│   ├── user_setup.py           # User customization hook
│   ├── cli/                    # CLI components
│   │   ├── __init__.py
│   │   ├── manager.py          # CLI manager
│   │   └── parser.py           # Argument parsers
│   ├── commands/               # Command implementations
│   │   ├── __init__.py
│   │   ├── checkout.py
│   │   ├── export.py
│   │   ├── test.py
│   │   ├── compile.py
│   │   └── xids.py
│   └── loaders/                # Loader implementations
│       ├── __init__.py
│       ├── loader.py           # Base loader classes
│       ├── project_loader.py   # Project loader base
│       └── <Project>.py        # Per-project loaders
├── toolkit/                    # Java source code
│   ├── src/
│   │   └── io/github/universetraveller/
│   │       ├── ant/           # Custom Ant tasks
│   │       ├── d4j/           # Defects4J tasks
│   │       └── util/          # Java utilities
│   ├── junit-agent/           # **EXPERIMENTAL** JUnit agent
│   ├── compile.sh             # Toolkit build script
│   └── target/
│       └── toolkit.jar        # Compiled toolkit
├── projects/                   # Bug metadata and patches
│   └── <Project>/
│       ├── bugs-registry.csv  # Bug registry
│       ├── <Project>.export.xml
│       ├── <Project>.compile.xml
│       └── patches/           # Bug-specific patches
├── resources/                  # Configuration resources
│   └── defects4j.properties
├── setup.py                    # Python package installer
├── setup_unix_user.py          # Unix setup script
├── c4j                         # Startup script
└── Dockerfile                  # Docker configuration
```

## Component Overview

### Python Components

#### 1. Bootstrap System (`_bootstrap.py`, `bootstrap.py`)

**Purpose**: Manages system initialization and component lifecycle.

**Key Responsibilities**:
- Define initialization order
- Register bootstrap functions
- Manage entry point
- Provide startup context

**Design Pattern**: Registry pattern with lazy initialization

**Two-Level Design**:
- `_bootstrap.py`: Low-level, immutable infrastructure
- `bootstrap.py`: High-level, user-customizable initialization

#### 2. Configuration System (`config.py`, `env.py`)

**Purpose**: Centralized configuration and environment management.

**Components**:
- `config.py`: Static configuration values
- `env.py`: Dynamic environment initialization

**Configuration Flow**:
```
config.py → SystemConfig (read-only)
                ↓
         Custom env init → SystemEnv (read-only)
                ↓
         Merged → SystemContext (read-only)
                ↓
         Copy → Context (modifiable)
```

**Key Features**:
- Read-only system objects prevent accidental modification
- Modifiable copies for command execution
- Caching for performance

#### 3. Command System (`commands/`, `dispatcher.py`)

**Purpose**: Implement and execute dataset operations.

**Architecture**:
```
User Input → CLI Parser → Dispatcher → ExecutionContext → Command Entry
                                            ↓
                                    Result ← Command Logic
```

**Command Registration**:
- Commands registered in `bootstrap.initialize_commands()`
- Dynamic command lookup via `get_entry()`
- Support for programmatic and CLI execution

**Execution Modes**:
- `CLI Mode`: Full output, file I/O, user feedback
- `API Mode`: Silent operation, return results only

#### 4. Loader System (`loaders/`)

**Purpose**: Handle project-specific operations and customizations.

**Hierarchy**:
```
Loader (base)
  ↓
ContextAwareLoader
  ↓
ProjectLoader (abstract)
  ↓
<Project>Loader (concrete)
```

**Responsibilities**:
- VCS operations (checkout, diff)
- Directory layout determination
- Property retrieval
- Post-checkout hooks
- Toolkit execution

**Lazy Loading**: Loaders are imported only when needed for performance.

#### 5. Utilities (`util.py`, `c4jutil.py`, `d4jutil.py`)

**Purpose**: Common operations and integration logic.

**Categories**:
- **File I/O**: Encoding-aware read/write with fallback
- **VCS**: Git operations (checkout, diff, tag)
- **Cache**: Performance optimization via file caching
- **Properties**: Java properties file handling
- **Task Printing**: Progress feedback for long operations
- **CatenaD4J Utils**: Version parsing, property access
- **Defects4J Utils**: Metadata extraction, compatibility

### Java Components (Toolkit)

#### 1. Ant Tasks (`toolkit/src/.../ant/`)

**Purpose**: Custom Ant task definitions for build operations.

**Key Tasks**:
- `CheckAndRename`: Conditional file renaming
- `AppendProperty`: Property manipulation
- `CheckTargetExists`: Dynamic target validation
- `FilterPath`: Path filtering based on existence
- `DynamicNoOpTask`: No-op placeholder

**Integration**: Loaded via Ant's `taskdef` in project build files.

#### 2. Defects4J Integration (`toolkit/src/.../d4j/`)

**Purpose**: Efficient property export and test execution.

**Components**:

##### `Defects4JExport`
- Exports static and dynamic properties
- Optimized build file processing
- Caching support
- Command: `java -cp ... Defects4JExport <build.xml> <property>`

##### `Defects4JTest`
- JUnit test execution with custom isolation
- Multiple isolation levels
- Failure collection
- Command: `java -cp ... Defects4JTest <build.xml> [tests...]`

##### `Defects4JExecute`
- Arbitrary Ant target execution
- Simplified build file processing
- Command: `java -cp ... Defects4JExecute <build.xml> <target>`

#### 3. Test Utilities (`toolkit/src/.../util/`)

**Purpose**: JUnit test isolation and execution.

**Components**:
- `JUnit4Helper`: Reused isolated classloader (fast)
- `JUnit4Helper1`: Per-class isolated classloader (balanced)
- `JUnit3Helper`: JUnit 3 compatibility
- `IsolatedClassLoader`: Custom classloader for isolation
- `ClassesCollector`: Test discovery
- `AntJUnitFormatter`: Result formatting

#### 4. JUnit Agent (`toolkit/junit-agent/`) - **EXPERIMENTAL FEATURE**

⚠️ **WARNING: EXPERIMENTAL** ⚠️

**Purpose**: Prevent failed JUnit assertions from halting test execution while preserving exception messages.

**Status**: Experimental - not recommended for production use

**Functionality**:
- Java agent that intercepts assertion failures
- Allows multiple assertions to fail in a single test
- Preserves stack traces and messages

**Usage**: Not currently integrated into main toolkit

**Future Work**: May be integrated for advanced fault localization

## Bootstrap Process

### Initialization Sequence

```
1. Import catena4j.bootstrap
         ↓
2. Register bootstrap functions
   - initialize_environment
   - initialize_cli
   - initialize_commands
   - initialize_loaders
   - initialize_user_setup
         ↓
3. Register entry point (start_cli)
         ↓
4. Register initialization order (initialize_system)
         ↓
5. Access system.start
         ↓
6. Execute initialize_system(system)
   a. system.initialize_environment
      - Load config.py → SystemConfig
      - Execute env constructor → SystemEnv
      - Merge → SystemContext
   b. system.initialize_cli
      - Create root parser
      - Add subcommands
      - Configure task printer
   c. system.initialize_commands
      - Register all command entries
   d. system.initialize_loaders
      - Register all project loaders (lazy)
   e. system.initialize_user_setup
      - Execute user_setup.py (hook)
         ↓
7. Execute entry point (start_cli)
   - Parse CLI arguments
   - Create dispatcher
   - Get execution context
   - Run target command
```

### Customization Points

Users can customize initialization by:

1. **Adding Bootstrap Functions**:
```python
from catena4j.bootstrap import register_bootstrap_function

def my_setup():
    # Custom initialization
    pass

register_bootstrap_function(my_setup)
```

2. **Changing Initialization Order**:
```python
from catena4j.bootstrap import initialize_system, register_initialization_order

def custom_order(system):
    system.my_setup  # Run first
    initialize_system(system)  # Then default

register_initialization_order(custom_order)
```

3. **Replacing Entry Point**:
```python
from catena4j.bootstrap import register_entry_point

def my_entry():
    # Custom main logic
    pass

register_entry_point(my_entry)
```

## Python-Java Integration

### Communication Mechanism

Python and Java communicate via subprocess execution:

```
Python Command
     ↓
Construct Java Command
     ↓
subprocess.run(java -cp ... MainClass args...)
     ↓
Java Execution
     ↓
Capture stdout/stderr
     ↓
Parse Result
     ↓
Return to Python
```

### Toolkit Execution

**Function**: `toolkit_execute()` in `util.py`

**Process**:
1. Locate toolkit JAR
2. Construct classpath (toolkit + Defects4J + Ant)
3. Build Java command with main class and arguments
4. Set system properties
5. Execute via subprocess
6. Capture and return output

**Example Java Command**:
```bash
java -cp toolkit.jar:defects4j/major/lib/*:... \
     -Dc4j.d4j.properties=/path/to/defects4j.properties \
     -Dbasedir=/work/dir \
     io.github.universetraveller.d4j.Defects4JExport \
     /path/to/build.xml \
     tests.all
```

### Performance Optimization

**Challenges**:
- JVM startup overhead
- Ant initialization cost
- File I/O

**Solutions**:
1. **Property Caching**: Cache computed properties to avoid re-execution
2. **Simplified Build Files**: Use minimal Ant targets
3. **Batch Operations**: Execute multiple operations in single JVM invocation
4. **Minimal Checkout**: Skip unnecessary Git operations

## Command Execution Flow

### CLI Flow

```
User: catena4j checkout -p Chart -v 15b1 -w ./work
         ↓
CLI Parser (RootArgumentParser)
         ↓
Extract command: "checkout"
Extract args: {p: 'Chart', v: '15b1', w: './work'}
         ↓
Dispatcher.run('checkout', args, cli=True)
         ↓
Create ExecutionContext (CLI mode)
         ↓
ExecutionContext.run('checkout')
         ↓
get_entry('checkout') → checkout.run
         ↓
checkout.run(context)
   - Parse version ID
   - Get project loader
   - Checkout via Defects4J
   - Apply CatenaD4J patches
   - Create commits/tags
         ↓
Print results to stdout
```

### API Flow

```python
from catena4j.dispatcher import CommandDispatcher
from argparse import Namespace

dispatcher = CommandDispatcher()
args = Namespace(p='Chart', v='15b1', w='./work')
result = dispatcher.run('checkout', args, cli=False)
```

```
Python Code
         ↓
Dispatcher.run('checkout', args, cli=False)
         ↓
Create ExecutionContext (API mode)
         ↓
ExecutionContext.run('checkout')
         ↓
checkout.run(context)
   - Same logic as CLI
   - No stdout output
         ↓
Return result directly
```

## Data Flow

### Bug Metadata Flow

```
projects/<Project>/bugs-registry.csv
         ↓
Read by c4jutil.get_bugs_registry()
         ↓
Parse CSV: project, bid, cid, loader
         ↓
Cache in context.c4j_cache
         ↓
Used by commands (checkout, export, etc.)
```

### Property Computation Flow

```
Command: export -p tests.trigger
         ↓
Identify property type:
  - CatenaD4J property?
  - Defects4J static?
  - Defects4J dynamic?
         ↓
[CatenaD4J Property]
         ↓
Read from projects/<Project>/patches/<bid>/<cid>/meta.json
         ↓
Return value

[Defects4J Static]
         ↓
Read from Defects4J repository:
  - d4j_home/framework/projects/<Project>/*.csv
         ↓
Return value

[Defects4J Dynamic]
         ↓
Execute Java Toolkit:
  java ... Defects4JExport build.xml <property>
         ↓
Ant processes build file
         ↓
Return computed value
```

### Version Control Flow

```
checkout command
         ↓
Get project loader
         ↓
loader.checkout_revision(revision_id, wd)
         ↓
VCS.checkout_revision(revision_id, wd)
         ↓
[Git]
git clone <repo_path> <wd>
git checkout <revision_id>
         ↓
loader.d4j_checkout_hook()
   - Project-specific modifications
         ↓
Apply CatenaD4J patches
   - Test modifications
   - Bug-specific changes
         ↓
Create commits and tags
```

## Extension Architecture

### Adding Custom Commands

**1. Define Command Function**:
```python
# catena4j/commands/mycommand.py
from ..dispatcher import ExecutionContext

def run(context: ExecutionContext):
    args = context.args
    # Command logic
    return result

def initialize():
    # Create CLI parser if needed
    pass
```

**2. Register Command**:
```python
# catena4j/bootstrap.py
def initialize_commands():
    # ... existing commands ...
    from .commands import mycommand
    mycommand.initialize()
    _register('mycommand', mycommand.run)
```

### Adding Custom Loaders

**1. Define Loader Class**:
```python
# catena4j/loaders/MyProject.py
from .project_loader import ProjectLoader
from ..util import Git

class MyProjectLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'MyProject'
    
    def determine_layout(self):
        return {
            'src': ['src/main/java'],
            'test': ['src/test/java']
        }
```

**2. Register Loader**:
```python
# catena4j/bootstrap.py
def initialize_loaders():
    # ... existing loaders ...
    register_project_loader('MyProject')
```

### Adding Java Toolkit Components

**1. Create Java Class**:
```java
// toolkit/src/.../MyTask.java
package io.github.universetraveller.ant;

import org.apache.tools.ant.Task;

public class MyTask extends Task {
    public void execute() {
        // Task logic
    }
}
```

**2. Compile and Package**:
```bash
cd toolkit
bash compile.sh
```

**3. Use in Build Files**:
```xml
<taskdef name="mytask" 
         classname="io.github.universetraveller.ant.MyTask"
         classpathref="d4j.classpath"/>
<mytask ... />
```

## Performance Considerations

### Bottlenecks

1. **JVM Startup**: Each toolkit invocation starts a new JVM
2. **Ant Processing**: Ant build file parsing and execution
3. **File I/O**: Reading metadata and properties
4. **VCS Operations**: Git operations (clone, checkout)

### Optimizations

1. **Caching**:
   - Property values cached in `.cache/`
   - Defects4J metadata cached in memory
   - Use `--from-cache` flag for repeated queries

2. **Minimal Operations**:
   - `minimal_checkout` skips unnecessary commits
   - Simplified Ant build files reduce processing
   - Lazy loader imports

3. **Batch Processing**:
   - Process multiple properties in one invocation when possible
   - Reuse execution contexts

4. **Parallel Execution**:
   - Commands are stateless and can run in parallel
   - Multiple working directories supported

### Performance Tips

**DO**:
- Use cache flags for repeated operations
- Batch operations when possible
- Use API mode for programmatic access
- Reuse working directories

**DON'T**:
- Repeatedly export the same property without cache
- Start multiple JVMs for single operations
- Use full history when not needed

## Architecture Decisions

### Why Python + Java?

**Python**:
- Rapid development
- Excellent scripting capabilities
- Easy CLI creation
- Rich ecosystem for data processing

**Java**:
- Defects4J compatibility (Ant-based)
- Performance for computation-intensive tasks
- JUnit integration
- Existing build system infrastructure

### Why Ant?

- Defects4J uses Ant extensively
- Mature build system with good Java support
- Extensible via custom tasks
- Compatible with existing project build files

### Why Modular Design?

- **Extensibility**: Users can add custom components
- **Testability**: Components can be tested independently
- **Maintainability**: Clear separation of concerns
- **Reusability**: Components can be used in different contexts

## Future Improvements

### Planned Enhancements

1. **Lightweight Test Runner**: Replace Ant-based testing with direct JUnit invocation
2. **Fast Checkout**: Re-implement checkout without Defects4J dependency
3. **Code Coverage Integration**: Add fast coverage tools
4. **SBFL Integration**: Built-in spectrum-based fault localization
5. **Complete D4J Replacement**: Remove Defects4J dependency entirely

### Experimental Features

**JUnit Agent** (`toolkit/junit-agent/`):
- Currently experimental
- May be integrated for advanced testing
- Enables non-failing assertion collection
- Requires further testing and validation

## See Also

- [User Guide](README.md) - Installation and usage
- [API Reference](API.md) - Programmatic interface
- [Component Guides](commands/README.md) - Detailed component docs
