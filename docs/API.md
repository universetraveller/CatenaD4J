# CatenaD4J API Reference

## Table of Contents
- [Introduction](#introduction)
- [Python API](#python-api)
  - [Bootstrap System](#bootstrap-system)
  - [Command Dispatcher](#command-dispatcher)
  - [Context Management](#context-management)
  - [Loaders](#loaders)
  - [Utilities](#utilities)
- [Java Toolkit API](#java-toolkit-api)
  - [Ant Tasks](#ant-tasks)
  - [Defects4J Integration](#defects4j-integration)
  - [Test Utilities](#test-utilities)
- [Extension Points](#extension-points)
- [Code Examples](#code-examples)

## Introduction

CatenaD4J provides both Python and Java APIs for programmatic access to its functionality. The Python API is the primary interface for dataset operations, while the Java toolkit provides performance-critical operations through Ant tasks.

## Python API

### Bootstrap System

The bootstrap system manages the initialization and startup of CatenaD4J.

#### Module: `catena4j._bootstrap`

Low-level system initialization APIs.

**Functions**:

##### `start()`
```python
def start() -> None
```
The main entry point of the program. Must be called after initialization functions are registered.

**Raises**:
- `BootstrapError`: If entry point or initialization order is not set

**Example**:
```python
from catena4j._bootstrap import start
start()
```

##### `register_bootstrap_function(f: Callable)`
```python
def register_bootstrap_function(f: Callable) -> None
```
Register a function to be called during system initialization.

**Parameters**:
- `f`: Function to register (must have a unique name)

**Raises**:
- `BootstrapError`: If function name is reserved

##### `register_entry_point(f: Callable)`
```python
def register_entry_point(f: Callable) -> None
```
Register the main entry point of the program.

**Parameters**:
- `f`: Function to use as entry point

##### `register_initialization_order(f: Callable)`
```python
def register_initialization_order(f: Callable) -> None
```
Register the initialization sequence function.

**Parameters**:
- `f`: Function that defines initialization order; receives `StartupContext` as parameter

**Classes**:

##### `StartupContext`
```python
class StartupContext(metaclass=_StartupContext)
```
Entry point for the system. Attributes are dynamically resolved to registered bootstrap functions.

**Usage**:
```python
from catena4j._bootstrap import StartupContext as system
system.start  # Triggers initialization and runs entry point
```

#### Module: `catena4j.bootstrap`

High-level initialization methods.

**Functions**:

##### `initialize_commands()`
```python
def initialize_commands() -> None
```
Register all built-in commands (export, checkout, test, compile, etc.).

##### `initialize_loaders()`
```python
def initialize_loaders() -> None
```
Register all project-specific loaders.

##### `start_cli()`
```python
def start_cli() -> None
```
Default entry point that parses CLI arguments and dispatches commands.

##### `initialize_system(system: StartupContext)`
```python
def initialize_system(system: StartupContext) -> None
```
Default initialization order for the system.

**Example - Custom Initialization**:
```python
from catena4j.bootstrap import (
    register_bootstrap_function,
    initialize_system,
    register_initialization_order,
    system
)

def custom_initialization():
    print('Custom setup')

register_bootstrap_function(custom_initialization)

def updated_order(sys):
    initialize_system(sys)
    sys.custom_initialization

register_initialization_order(updated_order)
system.start
```

### Command Dispatcher

#### Module: `catena4j.dispatcher`

**Classes**:

##### `CommandDispatcher`
```python
class CommandDispatcher:
    def __init__(self, context: Context = None)
    def get_execution_context(self, args: Namespace, cli: bool = False) -> ExecutionContext
    def run(self, target: str, args: Namespace, cli: bool = False) -> Any
```

Execute commands programmatically.

**Parameters**:
- `context`: System context (default: singleton instance)

**Methods**:

- `get_execution_context(args, cli)`: Create an execution context
  - `args`: Argument namespace
  - `cli`: Whether running in CLI mode
  - Returns: `ExecutionContext`

- `run(target, args, cli)`: Execute a command
  - `target`: Command name
  - `args`: Command arguments
  - `cli`: Whether running in CLI mode
  - Returns: Command result

**Example**:
```python
from catena4j.dispatcher import CommandDispatcher
from argparse import Namespace

dispatcher = CommandDispatcher()
args = Namespace(p='Chart', b='15')
result = dispatcher.run('bids', args, cli=False)
print(result)  # ['1', '2', '3', ...]
```

##### `ExecutionContext`
```python
class ExecutionContext(Context):
    CLI = 0  # Run as command line interface
    API = 1  # Standard output and file output ignored
    
    def __init__(self, args: Namespace, mode: int, dispatcher: CommandDispatcher)
    def run(self, target: str) -> Any
```

Context for command execution.

**Attributes**:
- `args`: Command arguments
- `mode`: Execution mode (CLI or API)
- `dispatcher`: Parent dispatcher
- Inherits all attributes from system context

### Context Management

#### Module: `catena4j.env`

**Functions**:

##### `initialize_config()`
```python
def initialize_config() -> None
```
Initialize the system configuration from `config.py`.

##### `initialize_env()`
```python
def initialize_env() -> None
```
Initialize the system environment variables.

##### `initialize_system_context()`
```python
def initialize_system_context() -> None
```
Create the merged system context from config and environment.

##### `get_system_config()`
```python
def get_system_config() -> SystemConfig
```
Get the read-only system configuration object.

**Returns**: Configuration with attributes from `config.py`

##### `get_system_env()`
```python
def get_system_env() -> SystemEnv
```
Get the read-only system environment object.

**Returns**: Environment with dynamically computed values

##### `get_system_context(copy: bool = True)`
```python
def get_system_context(copy: bool = True) -> Context | SystemContext
```
Get the system context (merged config and environment).

**Parameters**:
- `copy`: If True, return modifiable copy; if False, return read-only singleton

**Classes**:

##### `Context`
```python
class Context(Namespace):
    def as_dict(self) -> dict
    @staticmethod
    def get_instance() -> Context
    def copy(self) -> Context
```

Modifiable context inheriting from `argparse.Namespace`.

**Example**:
```python
from catena4j.env import get_system_context

context = get_system_context()
print(context.c4j_home)
print(context.d4j_home)
print(context.cli_program)

# Modify context
context.custom_attr = 'value'
```

### Loaders

#### Module: `catena4j.loaders`

**Functions**:

##### `register_loader(name: str, loader: Loader)`
```python
def register_loader(name: str, loader: Loader) -> None
```
Register a loader class.

**Parameters**:
- `name`: Loader identifier
- `loader`: Loader class (not instance)

**Raises**:
- `LoaderError`: If loader already registered

##### `register_loader_lazy(name: str, package: str, clazz: str, level: int)`
```python
def register_loader_lazy(name: str, package: str, clazz: str, level: int) -> None
```
Register a loader with lazy import (performance optimization).

**Parameters**:
- `name`: Loader identifier
- `package`: Package name
- `clazz`: Class name
- `level`: Import level (1 for relative imports)

##### `get_loader(name: str)`
```python
def get_loader(name: str) -> type[Loader]
```
Get a registered loader class.

**Returns**: Loader class

**Raises**:
- `LoaderError`: If loader not found

##### `get_project_loader(proj: str)`
```python
def get_project_loader(proj: str) -> type[ProjectLoader]
```
Get the loader for a specific project.

**Parameters**:
- `proj`: Project name

**Returns**: Project loader class

**Raises**:
- `LoaderError`: If no loader found

##### `set_project_loader(proj: str, loader: str)`
```python
def set_project_loader(proj: str, loader: str) -> None
```
Override the loader used for a project.

**Parameters**:
- `proj`: Project name
- `loader`: Loader name to use

**Classes**:

##### `Loader`
```python
class Loader:
    pass
```

Base loader class (marker interface).

##### `ContextAwareLoader`
```python
class ContextAwareLoader(Loader):
    def __init__(self, context: ExecutionContext)
```

Base class for loaders that need context access.

**Attributes**:
- `context`: Execution context

##### `ProjectLoader`
```python
class ProjectLoader(ContextAwareLoader):
    version_control_system_class = None  # Must be set by subclass
    project_name = None  # Must be set by subclass
    
    def checkout_revision(self, revision_id: str, wd: str) -> Any
    def export_diff(self, a: str, b: str, output: Path = None) -> str
    def get_property(self, name: str, project: str, bid: str, cid: str) -> str
    def load_buggy_version(self, project: str, bid: str, cid: str, wd: str) -> None
    def load_fixed_version(self, project: str, bid: str, cid: str, wd: str) -> None
    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str) -> bool
    def determine_layout(self) -> dict
    def toolkit_execute(self, target: Any, project: str, wd: str, **kwargs) -> str
```

Abstract base class for project-specific loaders.

**Must Override**:
- `version_control_system_class`: VCS class (e.g., `Git`, `Svn`)
- `project_name`: Project identifier
- `determine_layout()`: Return dict with 'src' and 'test' directory layouts

**Methods**:
- `checkout_revision(revision_id, wd)`: Check out a specific VCS revision
- `export_diff(a, b, output)`: Export diff between two revisions
- `get_property(name, project, bid, cid)`: Get a CatenaD4J property
- `load_buggy_version(...)`: Apply patches for buggy version
- `load_fixed_version(...)`: Apply patches for fixed version
- `d4j_checkout_hook(...)`: Project-specific post-checkout tasks
- `toolkit_execute(...)`: Execute Java toolkit operations

**Example - Custom Loader**:
```python
from catena4j.loaders import ProjectLoader, register_loader
from catena4j.util import Git

class MyProjectLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'MyProject'
    
    def determine_layout(self):
        return {
            'src': ['src/main/java'],
            'test': ['src/test/java']
        }
    
    def d4j_checkout_hook(self, project, revision_id, wd):
        # Custom post-checkout logic
        return False

register_loader('MyProject', MyProjectLoader)
```

### Utilities

#### Module: `catena4j.util`

**File I/O Functions**:

##### `read_file(file: Path, encoding: str = None)`
```python
def read_file(file: Path, encoding: str = None) -> str | None
```
Read file with automatic encoding detection.

**Parameters**:
- `file`: Path to file
- `encoding`: Specific encoding (default: try utf-8, then latin-1)

**Returns**: File contents or None if file doesn't exist

##### `write_file(file: Path, content: str, encoding: str = None)`
```python
def write_file(file: Path, content: str, encoding: str = None) -> None
```
Write file with automatic encoding handling. Creates parent directories if needed.

**Parameters**:
- `file`: Path to file
- `content`: Content to write
- `encoding`: Specific encoding (default: try utf-8, then latin-1)

##### `append_file(file: Path, content: str, encoding: str = None)`
```python
def append_file(file: Path, content: str, encoding: str = None) -> None
```
Append to file with automatic encoding handling.

**Cache Functions**:

##### `get_cache_path(context: Namespace, *parts)`
```python
def get_cache_path(context: Namespace, *parts) -> Path
```
Construct cache file path.

**Parameters**:
- `context`: System context
- `*parts`: Path components

**Returns**: Path to cache file

##### `search_cache(cache: Path, check: Callable = None, fix: Callable = None, args=(), kwargs={})`
```python
def search_cache(cache: Path, check: Callable = None, fix: Callable = None, 
                 args=(), kwargs={}) -> Any
```
Find result from cache or compute and store it.

**Parameters**:
- `cache`: Cache file path
- `check`: Function to validate cached result
- `fix`: Function to compute result on cache miss
- `args`, `kwargs`: Arguments for fix function

**Returns**: Cached or computed result

**Raises**:
- `Catena4JError`: On cache miss without fix function

**Properties Functions**:

##### `read_properties(file: Path)`
```python
def read_properties(file: Path) -> dict | None
```
Read Java properties file.

**Returns**: Dictionary of properties or None

##### `write_properties(file: Path, props: dict)`
```python
def write_properties(file: Path, props: dict) -> None
```
Write Java properties file.

**Task Printer**:

##### `TaskPrinter`
```python
class TaskPrinter:
    def __init__(self, message: str)
    def __enter__(self) -> TaskPrinter
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool
    
    @staticmethod
    def configurate(start: str, done: str, fail: str, anchor: int, padding: str)
```

Context manager for printing task progress with status indicators.

**Example**:
```python
from catena4j.util import TaskPrinter

with TaskPrinter("Compiling project") as printer:
    # Long-running task
    compile_project()
# Prints: "Compiling project.................... DONE" or "FAILED"
```

**VCS Classes**:

##### `Git`
```python
class Git:
    def __init__(self, loader: ProjectLoader)
    def checkout_revision(self, revision_id: str, wd: str) -> subprocess.CompletedProcess
    def export_diff(self, a: str, b: str, output: Path = None) -> str
    @staticmethod
    def format_name(name: str) -> str
```

Git version control operations.

**Methods**:
- `checkout_revision(revision_id, wd)`: Check out a specific commit
- `export_diff(a, b, output)`: Generate diff between commits
- `format_name(name)`: Format repository name (appends `.git`)

#### Module: `catena4j.c4jutil`

CatenaD4J-specific utility functions.

##### `read_version_info(wd: str, context: Context)`
```python
def read_version_info(wd: str, context: Context) -> dict
```
Read version information from a working directory.

**Returns**: Dict with keys `pid`, `bid`, `cid`, `tag`

**Raises**:
- `Catena4JError`: If not a valid working directory

##### `parse_vid(vid: str)`
```python
def parse_vid(vid: str) -> tuple[str, str, str]
```
Parse version ID string.

**Parameters**:
- `vid`: Version ID in format `<bid><b/f><cid>`

**Returns**: Tuple of `(bid, tag, cid)` where tag is 'b' or 'f'

**Example**:
```python
bid, tag, cid = parse_vid('15b1')  # ('15', 'b', '1')
```

##### `get_property(name: str, project: str, bid: str, cid: str, context: Context)`
```python
def get_property(name: str, project: str, bid: str, cid: str, context: Context) -> str
```
Get a CatenaD4J property value.

**Parameters**:
- `name`: Property name
- `project`: Project name
- `bid`: Bug ID
- `cid`: Catena ID
- `context`: System context

**Returns**: Property value

#### Module: `catena4j.d4jutil`

Defects4J integration utilities.

##### `get_classes_modified(project: str, bid: str, context: Context)`
```python
def get_classes_modified(project: str, bid: str, context: Context) -> list[str]
```
Get classes modified by a bug fix.

**Returns**: List of fully-qualified class names

##### `get_tests_trigger(project: str, bid: str, context: Context)`
```python
def get_tests_trigger(project: str, bid: str, context: Context) -> list[str]
```
Get trigger tests for a bug.

**Returns**: List of test identifiers

##### `get_active_bugs(project: str, context: Context)`
```python
def get_active_bugs(project: str, context: Context) -> dict
```
Get all active bugs for a project.

**Returns**: Dict mapping bug IDs to metadata

## Java Toolkit API

The Java toolkit provides Ant tasks for performance-critical operations.

### Ant Tasks

#### Package: `io.github.universetraveller.ant`

##### `CheckAndRename`
```java
public class CheckAndRename extends Task
```
Ant task to check if a target exists and rename it.

**Attributes**:
- `from`: Source path
- `to`: Destination path
- `check`: Path to check for existence

##### `DynamicNoOpTask`
```java
public class DynamicNoOpTask extends Task
```
Placeholder task that does nothing. Used for dynamic task resolution.

##### `AppendProperty`
```java
public class AppendProperty extends Task
```
Append a value to a property with a separator.

**Attributes**:
- `name`: Property name
- `value`: Value to append
- `separator`: Separator character (default: ',')

##### `CheckTargetExists`
```java
public class CheckTargetExists extends Task
```
Check if an Ant target exists in the project.

**Attributes**:
- `target`: Target name to check
- `property`: Property to set if target exists

##### `FilterPath`
```java
public class FilterPath extends Task
```
Filter path elements based on existence.

**Attributes**:
- `pathid`: ID of path to filter
- `outputid`: ID for filtered result

### Defects4J Integration

#### Package: `io.github.universetraveller.d4j`

##### `Defects4JExport`
```java
public class Defects4JExport extends Defects4JStartup
```
Main class for exporting Defects4J properties.

**Constructor**:
```java
public Defects4JExport(String projectBuildFile)
```

**Main Method**:
```java
public static void main(String[] args)
```
Args: `<project_build_file> <property_name> [output_file]`

**Exported Properties**:
- Static: `classes.modified`, `classes.relevant`, `tests.trigger`, etc.
- Dynamic: `cp.compile`, `cp.test`, `tests.all`, etc.

##### `Defects4JTest`
```java
public class Defects4JTest extends AbstractDefects4JTest
```
Main class for running JUnit tests with custom isolation.

**Constructor**:
```java
public Defects4JTest(String projectBuildFile)
```

**Main Method**:
```java
public static void main(String[] args)
```
Args: `<project_build_file> [test_class#method ...]`

**System Properties**:
- `c4j.test.helper`: Test helper class (for isolation level 1 or 2)
- `c4j.test.runner`: Set to 'ant' for isolation level 3
- `OUTFILE`: File to write failing tests
- `c4j.tests.printer.out`: File to list all tests (list mode)

##### `Defects4JExecute`
```java
public class Defects4JExecute extends Defects4JStartup
```
Execute arbitrary Ant targets.

**Main Method**:
```java
public static void main(String[] args)
```
Args: `<project_build_file> <target_name>`

### Test Utilities

#### Package: `io.github.universetraveller.util`

##### `JUnit4Helper`
```java
public class JUnit4Helper
```
JUnit 4 test runner with reused isolated classloader (isolation level 1).

**Methods**:
```java
public static void main(String[] args)
```

##### `JUnit4Helper1`
```java
public class JUnit4Helper1
```
JUnit 4 test runner with per-class isolated classloader (isolation level 2).

##### `JUnit3Helper`
```java
public class JUnit3Helper
```
JUnit 3 test runner with isolation support.

##### `IsolatedClassLoader`
```java
public class IsolatedClassLoader extends URLClassLoader
```
Custom classloader for test isolation.

**Constructor**:
```java
public IsolatedClassLoader(URL[] urls, ClassLoader parent)
```

##### `ClassesCollector`
```java
public class ClassesCollector
```
Utility to collect test classes from directory.

**Methods**:
```java
public static List<String> collectTestClasses(File dir, String pattern)
```

## Extension Points

### Custom Commands

Register custom commands during initialization:

```python
from catena4j.commands import register
from catena4j.bootstrap import register_bootstrap_function

def my_command(context):
    """Custom command implementation"""
    args = context.args
    # Command logic here
    return result

def initialize_my_commands():
    register('mycommand', my_command)

register_bootstrap_function(initialize_my_commands)
```

### Custom Loaders

Create project-specific loaders:

```python
from catena4j.loaders import ProjectLoader, register_loader
from catena4j.util import Git

class CustomProjectLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'CustomProject'
    
    def determine_layout(self):
        return {
            'src': ['src/main/java', 'src/main/resources'],
            'test': ['src/test/java']
        }
    
    def d4j_checkout_hook(self, project, revision_id, wd):
        # Project-specific logic
        return False

def initialize_custom_loaders():
    register_loader('CustomProject', CustomProjectLoader)

from catena4j.bootstrap import register_bootstrap_function
register_bootstrap_function(initialize_custom_loaders)
```

### Environment Customization

Override environment initialization:

```python
from catena4j.env import register_env_constructor

def custom_env_init():
    return {
        'custom_var': 'value',
        # ... other environment variables
    }

register_env_constructor(custom_env_init)
```

## Code Examples

### Example 1: Programmatic Checkout

```python
from catena4j.dispatcher import CommandDispatcher
from argparse import Namespace

dispatcher = CommandDispatcher()

# Checkout a bug
checkout_args = Namespace(
    p='Chart',
    v='15b1',
    w='./workspace/chart_15b1',
    full_history=False
)
dispatcher.run('checkout', checkout_args)

# Compile it
compile_args = Namespace(
    w='./workspace/chart_15b1',
    target='compile.tests',
    verbose=False
)
dispatcher.run('compile', compile_args)

# Run tests
test_args = Namespace(
    w='./workspace/chart_15b1',
    c=False,
    l=False,
    i=1,
    t=None,
    r=False,
    trigger=True,
    a=False
)
result = dispatcher.run('test', test_args)
print(f"Test result: {result}")
```

### Example 2: Query Dataset Information

```python
from catena4j.dispatcher import CommandDispatcher
from catena4j.commands.xids import query_pids, query_bids, query_cids
from catena4j.env import get_system_context

context = get_system_context()

# Get all projects
projects = query_pids(context)
print(f"Projects: {projects}")

# Get bugs for each project
for project in projects:
    bugs = query_bids(project, context)
    print(f"{project}: {len(bugs)} bugs")
    
    # Get catena IDs for first bug
    if bugs:
        cids = query_cids(project, list(bugs)[0], context)
        print(f"  Catena IDs for bug {list(bugs)[0]}: {cids}")
```

### Example 3: Export Properties Programmatically

```python
from catena4j.commands.export import query_c4j, query_d4j_static, query_d4j_dynamic
from catena4j.env import get_system_context

context = get_system_context()
wd = './workspace/chart_15b1'

# Get trigger tests
trigger_tests = query_c4j('tests.trigger', 'Chart', '15', '1', wd, context)
print(f"Trigger tests:\n{trigger_tests}")

# Get modified classes
modified = query_d4j_static('classes.modified', 'Chart', '15', wd, context)
print(f"Modified classes:\n{modified}")

# Get compile classpath
classpath = query_d4j_dynamic('cp.compile', 'Chart', wd, context)
print(f"Compile classpath:\n{classpath}")
```

### Example 4: Custom Initialization

```python
from catena4j.bootstrap import (
    register_bootstrap_function,
    initialize_system,
    register_initialization_order,
    system
)

def setup_logging():
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info("CatenaD4J initialized")

register_bootstrap_function(setup_logging)

def custom_init_order(sys):
    sys.setup_logging  # Run first
    initialize_system(sys)  # Then run default initialization

register_initialization_order(custom_init_order)

# Start the system
system.start
```

### Example 5: Using Context and Loaders

```python
from catena4j.env import get_system_context
from catena4j.loaders import get_project_loader

context = get_system_context()

# Get loader for a project
ChartLoader = get_project_loader('Chart')
loader = ChartLoader(context)

# Get property
prop = loader.get_property('tests.trigger', 'Chart', '15', '1')
print(f"Trigger tests: {prop}")

# Access VCS
src_layout = loader.src_layout
test_layout = loader.test_layout
print(f"Source layout: {src_layout}")
print(f"Test layout: {test_layout}")
```

## See Also

- [User Guide](README.md) - Command-line usage
- [Architecture](ARCHITECTURE.md) - System design
- [Component Guides](loaders.md) - Detailed component documentation
