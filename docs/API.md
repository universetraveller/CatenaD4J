# CatenaD4J Python API Documentation

This document provides detailed API documentation for the Python codebase of CatenaD4J, enabling programmatic access to dataset functionality.

## Table of Contents

- [Overview](#overview)
- [Core Modules](#core-modules)
- [Commands API](#commands-api)
- [Loaders API](#loaders-api)
- [Utilities API](#utilities-api)
- [Examples](#examples)

## Overview

The CatenaD4J Python API is organized into several modules:

- `catena4j.bootstrap`: Entry point and initialization
- `catena4j.commands`: Command implementations
- `catena4j.loaders`: Project-specific loaders
- `catena4j.util`: Utility functions
- `catena4j.c4jutil`: CatenaD4J-specific utilities
- `catena4j.d4jutil`: Defects4J integration utilities
- `catena4j.dispatcher`: Command execution management
- `catena4j.cli`: Command-line interface components

## Core Modules

### catena4j.bootstrap

Entry point for the CatenaD4J system.

#### Module: `bootstrap.py`

**Functions:**

```python
def system.start()
```
Main entry point for the CatenaD4J application. Initializes the system and starts command processing.

**Example:**
```python
from catena4j.bootstrap import system
system.start()
```

### catena4j.dispatcher

Manages command execution context and dispatching.

#### Class: `ExecutionContext`

Represents the execution environment for commands.

**Attributes:**
- `args`: Parsed command-line arguments
- `cwd`: Current working directory
- `c4j_home`: CatenaD4J installation directory
- `mode`: Execution mode (CLI or programmatic)

**Constants:**
- `ExecutionContext.CLI`: CLI execution mode

**Example:**
```python
from catena4j.dispatcher import ExecutionContext

context = ExecutionContext()
context.cwd = '/path/to/working/directory'
```

#### Class: `CommandDispatcher`

Dispatches commands to their respective handlers.

**Methods:**
```python
def dispatch(command_name: str, context: ExecutionContext)
```
Execute a command with the given context.

## Commands API

All commands follow a similar pattern: they accept an `ExecutionContext` and execute their logic based on the context's arguments.

### catena4j.commands.checkout

Check out a bug version to a working directory.

#### Function: `run(context: ExecutionContext)`

**Arguments (via context.args):**
- `p`: Project name
- `v`: Version ID in format `<bid><b/f><cid>`
- `w`: Working directory path
- `full_history`: (Optional) Generate full commit history

**Returns:** None

**Raises:**
- `Catena4JError`: If checkout fails

**Example:**
```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import checkout
from argparse import Namespace

context = ExecutionContext()
context.args = Namespace(
    p='Chart',
    v='15b1',
    w='./buggy',
    full_history=False
)
checkout.run(context)
```

### catena4j.commands.export

Export version-specific properties from a checked-out bug.

#### Function: `run(context: ExecutionContext) -> str`

**Arguments (via context.args):**
- `p`: Property name
- `w`: (Optional) Working directory
- `o`: (Optional) Output file path
- `from_cache`: (Optional) Use cached value if available
- `update_cache`: (Optional) Force cache update

**Returns:** Property value as string

**Raises:**
- `Catena4JError`: If property is unknown or export fails

**Example:**
```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import export
from argparse import Namespace

context = ExecutionContext()
context.args = Namespace(
    p='tests.trigger',
    w='./buggy',
    o=None,
    from_cache=False,
    update_cache=False
)
result = export.run(context)
print(result)
```

#### Helper Functions:

```python
def query_c4j(prop: str, proj: str, bid: str, cid: str, wd: str, 
              context: ExecutionContext = None, vtag: str = None) -> str
```
Query CatenaD4J-specific properties.

```python
def query_d4j_static(prop: str, proj: str, bid: str, wd: str,
                     context: ExecutionContext = None, vtag: str = None) -> str
```
Query static Defects4J properties.

```python
def query_d4j_dynamic(prop: str, proj: str, wd: str,
                      context: ExecutionContext = None) -> str
```
Query dynamic Defects4J properties (requires build file processing).

### catena4j.commands.xids

List available IDs (project IDs, bug IDs, catena IDs).

#### Functions:

```python
def run_pids(context: ExecutionContext) -> list
```
Get all available project IDs.

```python
def run_bids(context: ExecutionContext) -> list
```
Get all bug IDs for a project.

**Arguments (via context.args):**
- `p`: Project name

```python
def run_cids(context: ExecutionContext) -> list
```
Get all catena IDs for a specific bug.

**Arguments (via context.args):**
- `p`: Project name
- `b`: Bug ID

**Example:**
```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import xids
from argparse import Namespace

# Get project IDs
context = ExecutionContext()
projects = xids.run_pids(context)
print(projects)  # ['Chart', 'Cli', 'Closure', ...]

# Get bug IDs for a project
context.args = Namespace(p='Chart')
bugs = xids.run_bids(context)
print(bugs)  # [1, 2, 3, ...]

# Get catena IDs for a bug
context.args = Namespace(p='Chart', b='15')
catenas = xids.run_cids(context)
print(catenas)  # [1, 2, 3]
```

## Loaders API

Loaders are responsible for project-specific behavior during bug checkout and property export.

### catena4j.loaders.loader

Base loader classes.

#### Class: `Loader`

Base class for all loaders.

#### Class: `ContextAwareLoader(Loader)`

Base class for loaders that need access to execution context.

**Constructor:**
```python
def __init__(self, context: ExecutionContext)
```

**Attributes:**
- `context`: ExecutionContext instance

### catena4j.loaders.project_loader

Project-specific loader implementations.

#### Class: `ProjectLoader(ContextAwareLoader)`

Base class for project-specific loaders with common functionality.

**Methods:**

```python
def get_property(self, prop: str, proj: str, bid: str, cid: str) -> str
```
Get a project-specific property value.

```python
def toolkit_execute(self, prop: str, proj: str, wd: str, 
                   xml_attr: str = None, main_attr: str = None) -> str
```
Execute Java toolkit to compute dynamic properties.

**Parameters:**
- `prop`: Property name
- `proj`: Project name
- `wd`: Working directory
- `xml_attr`: XML build file attribute name
- `main_attr`: Java main class attribute name

### Getting a Project Loader

```python
from catena4j.loaders import get_project_loader

# Get loader class for a project
LoaderClass = get_project_loader('Chart')

# Instantiate with context
loader = LoaderClass(context)

# Use the loader
result = loader.get_property('tests.trigger', 'Chart', '15', '1')
```

### Available Project Loaders

The following project-specific loaders are available:

- `Chart`
- `Cli`
- `Closure`
- `Codec`
- `Collections`
- `Compress`
- `Csv`
- `Gson`
- `JacksonCore`
- `JacksonDatabind`
- `JacksonXml`
- `Jsoup`
- `JxPath`
- `Lang`
- `Math`
- `Mockito`
- `Time`

Each loader may override default behavior for project-specific requirements.

## Utilities API

### catena4j.util

General utility functions for file I/O, process execution, and more.

#### File Operations

```python
def read_file(file: Path, encoding: str = None) -> str
```
Read a file with automatic encoding detection.

**Parameters:**
- `file`: Path to file
- `encoding`: (Optional) Specific encoding to use

**Returns:** File contents as string or None if file doesn't exist

```python
def write_file(file: Path, content: str, encoding: str = None)
```
Write content to a file with automatic encoding handling.

**Parameters:**
- `file`: Path to file
- `content`: String content to write
- `encoding`: (Optional) Specific encoding to use

```python
def append_file(file: Path, content: str, encoding: str = None)
```
Append content to a file.

#### Property Files

```python
def read_properties(file: Path) -> dict
```
Read a Java-style properties file.

**Returns:** Dictionary of property key-value pairs

```python
def write_properties(file: Path, properties: dict)
```
Write properties to a file in Java format.

#### Process Execution

```python
class Git:
    """Git operations wrapper"""
    
    @staticmethod
    def clone(repo_url: str, target_dir: Path, *args)
    
    @staticmethod
    def checkout(ref: str, working_dir: Path)
    
    @staticmethod
    def apply_patch(patch_file: Path, working_dir: Path)
    
    @staticmethod
    def create_tag(tag_name: str, working_dir: Path)
```

#### Cache Management

```python
def get_cache_path(context: Namespace, *parts) -> Path
```
Get the path to a cache file.

```python
def search_cache(cache: Path, check: Callable = None, 
                fix: Tuple = None, args=(), kwargs={})
```
Search for a value in cache or compute and store it.

### catena4j.c4jutil

CatenaD4J-specific utility functions.

#### Version Parsing

```python
def parse_vid(vid: str) -> dict
```
Parse a version ID string into components.

**Parameters:**
- `vid`: Version ID string (e.g., '15b1')

**Returns:** Dictionary with keys:
- `bid`: Bug ID
- `tag`: 'b' or 'f' (buggy/fixed)
- `cid`: Catena ID

**Example:**
```python
from catena4j.c4jutil import parse_vid

info = parse_vid('15b1')
# {'bid': '15', 'tag': 'b', 'cid': '1'}
```

```python
def read_version_info(wd: Path, context: ExecutionContext) -> dict
```
Read version information from a working directory.

**Returns:** Dictionary with keys:
- `pid`: Project ID
- `bid`: Bug ID
- `tag`: Version tag ('b' or 'f')
- `cid`: Catena ID

```python
def check_vid(vid: str) -> bool
```
Validate a version ID string.

#### Git Operations

```python
def init_git_repository(wd: Path)
```
Initialize a git repository in a directory.

```python
def create_commit_and_tag(wd: Path, message: str, tag: str)
```
Create a git commit and tag it.

```python
def get_tag_name_from_ver(ver: str) -> str
```
Convert a version string to a git tag name.

#### Constants

```python
BUGGY = 'b'
FIXED = 'f'
ERR = -1
```

### catena4j.d4jutil

Defects4J integration utilities.

#### Bug Information

```python
def get_classes_modified(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of modified classes for a bug.

```python
def get_tests_trigger(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of trigger tests for a bug.

```python
def get_classes_relevant(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of relevant classes for a bug.

```python
def get_tests_relevant(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of relevant tests for a bug.

#### Directory Information

```python
def get_dir_src_classes(proj: str, bid: str, is_buggy: bool, 
                        context: ExecutionContext) -> str
```
Get source directory for classes.

```python
def get_dir_src_tests(proj: str, bid: str, is_buggy: bool,
                      context: ExecutionContext) -> str
```
Get source directory for tests.

#### Patch Operations

```python
def get_src_patch_dir(proj: str, context: ExecutionContext) -> Path
```
Get directory containing patch files for a project.

```python
def get_revision_id(proj: str, bid: str, is_buggy: bool,
                   context: ExecutionContext) -> str
```
Get git revision ID for a bug version.

```python
def fill_properties(props_file: Path, proj: str, bid: str, cid: str,
                   context: ExecutionContext)
```
Fill properties file with bug metadata.

## Examples

### Example 1: Programmatically Checkout and Export

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import checkout, export
from argparse import Namespace
from pathlib import Path

# Initialize context
context = ExecutionContext()

# Checkout a bug
context.args = Namespace(
    p='Chart',
    v='15b1',
    w='/tmp/chart15',
    full_history=False
)
checkout.run(context)

# Export trigger tests
context.args = Namespace(
    p='tests.trigger',
    w='/tmp/chart15',
    o=None,
    from_cache=False,
    update_cache=False
)
trigger_tests = export.run(context)
print("Trigger tests:", trigger_tests)

# Export modified classes
context.args.p = 'classes.modified'
modified_classes = export.run(context)
print("Modified classes:", modified_classes)
```

### Example 2: Batch Process Multiple Bugs

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import xids, checkout, export
from argparse import Namespace
from pathlib import Path

context = ExecutionContext()

# Get all projects
projects = xids.run_pids(context)

for project in projects[:3]:  # Process first 3 projects
    print(f"Processing project: {project}")
    
    # Get bugs for project
    context.args = Namespace(p=project)
    bugs = xids.run_bids(context)
    
    for bug in bugs[:2]:  # Process first 2 bugs
        # Get catena IDs
        context.args = Namespace(p=project, b=str(bug))
        cids = xids.run_cids(context)
        
        for cid in cids:
            version_id = f"{bug}b{cid}"
            work_dir = f"/tmp/{project}_{bug}_{cid}"
            
            print(f"  Checking out {project}-{version_id}")
            
            # Checkout
            context.args = Namespace(
                p=project,
                v=version_id,
                w=work_dir,
                full_history=False
            )
            checkout.run(context)
            
            # Export properties
            for prop in ['tests.trigger', 'classes.modified']:
                context.args = Namespace(
                    p=prop,
                    w=work_dir,
                    o=None,
                    from_cache=True,
                    update_cache=False
                )
                result = export.run(context)
                print(f"    {prop}: {len(result.split())} items")
```

### Example 3: Using Loaders Directly

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.loaders import get_project_loader

# Initialize context
context = ExecutionContext()

# Get Chart project loader
ChartLoader = get_project_loader('Chart')
loader = ChartLoader(context)

# Get property directly
trigger_tests = loader.get_property('tests.trigger', 'Chart', '15', '1')
print(trigger_tests)
```

### Example 4: Working with Cache

```python
from catena4j.util import get_cache_path, read_file, write_file
from catena4j.dispatcher import ExecutionContext
from pathlib import Path

context = ExecutionContext()

# Get cache path for a property
cache_path = get_cache_path(context, 'export', 'Chart', '15', '1', 'tests.trigger')

# Check if cache exists
cached_value = read_file(cache_path)
if cached_value:
    print("Using cached value:", cached_value)
else:
    # Compute value and cache it
    value = "org.jfree.chart.ChartTest::test1\norg.jfree.chart.ChartTest::test2"
    write_file(cache_path, value)
    print("Computed and cached:", value)
```

### Example 5: Custom Command Implementation

```python
from catena4j.cli.manager import create_command
from catena4j.dispatcher import ExecutionContext

def my_custom_command(context: ExecutionContext):
    """Custom command implementation"""
    args = context.args
    print(f"Running custom command with args: {args}")
    
    # Your custom logic here
    # Access args.p, args.v, etc.
    
    return "Success"

# Register command
parser = create_command('mycmd', help='My custom command')
parser.add_argument('-p', required=True)
parser.add_argument('-v', required=True)

# The command would be available as: catena4j mycmd -p Chart -v 15b1
```

## Error Handling

### Exception: `Catena4JError`

Base exception for CatenaD4J-specific errors.

```python
from catena4j.exceptions import Catena4JError

try:
    # Some operation
    result = export.run(context)
except Catena4JError as e:
    print(f"CatenaD4J error: {e}")
```

### Common Error Scenarios

1. **Invalid version ID**: Raised when version format is incorrect
2. **Missing working directory**: Raised when working directory doesn't exist or isn't a valid checkout
3. **Unknown property**: Raised when requesting a non-existent property
4. **Loader not found**: Raised when project loader is unavailable

## Best Practices

1. **Always initialize context**: Create a proper ExecutionContext with required attributes
2. **Use cache when appropriate**: Enable caching for expensive operations
3. **Handle exceptions**: Wrap API calls in try-except blocks
4. **Clean up resources**: Remove temporary working directories after use
5. **Validate inputs**: Check version IDs and property names before use
6. **Use loaders for project-specific logic**: Don't hardcode project behavior

## Advanced Topics

### Extending with Custom Loaders

To create a custom loader:

```python
from catena4j.loaders.project_loader import ProjectLoader

class MyProjectLoader(ProjectLoader):
    def get_property(self, prop, proj, bid, cid):
        # Custom property logic
        if prop == 'my.custom.property':
            return self._get_custom_property(proj, bid, cid)
        return super().get_property(prop, proj, bid, cid)
    
    def _get_custom_property(self, proj, bid, cid):
        # Your implementation
        return "custom value"
```

### Accessing Internal APIs

For advanced use cases, you can access internal modules:

```python
from catena4j.bootstrap import system
from catena4j.config import Config
from catena4j.env import Environment

# Access configuration
config = Config()

# Access environment
env = Environment()
```

## Further Reading

- [Usage Guide](USAGE.md) - End-user command-line documentation
- [Java Toolkit API](JAVA_API.md) - Java API documentation
- [Main README](../README.md) - Project overview
- [Scripts Documentation](../scripts/README.md) - Experimental reproduction
