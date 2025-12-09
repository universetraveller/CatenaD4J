# Python Commands API

This document covers the command implementations in CatenaD4J's Python API.

## Overview

Commands are the main entry points for CatenaD4J operations. They accept an `ExecutionContext` and execute their logic based on context arguments.

Package: `catena4j.commands`

## Core Module: catena4j.dispatcher

### Class: `ExecutionContext`

Represents the execution environment for commands.

**Attributes:**
- `args`: Parsed command-line arguments (Namespace object)
- `cwd`: Current working directory (str)
- `c4j_home`: CatenaD4J installation directory (str)
- `mode`: Execution mode (CLI or programmatic)

**Constants:**
- `ExecutionContext.CLI`: CLI execution mode constant

**Example:**
```python
from catena4j.dispatcher import ExecutionContext

context = ExecutionContext()
context.cwd = '/path/to/working/directory'
```

## checkout

Check out a bug version to a working directory.

**Module:** `catena4j.commands.checkout`

### Function: `run(context: ExecutionContext)`

**Arguments (via context.args):**
- `p` (str): Project name
- `v` (str): Version ID in format `<bid><b/f><cid>`
- `w` (str): Working directory path
- `full_history` (bool): Generate full commit history (optional)

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

**What it does:**
1. Validates version ID format
2. Creates working directory if needed
3. Uses Defects4J backend to checkout base bug
4. Applies catena-specific patches
5. Initializes git repository with tags
6. Saves version metadata

## export

Export version-specific properties from a checked-out bug.

**Module:** `catena4j.commands.export`

### Function: `run(context: ExecutionContext) -> str`

**Arguments (via context.args):**
- `p` (str): Property name
- `w` (str): Working directory (optional, defaults to current)
- `o` (str): Output file path (optional, defaults to stdout)
- `from_cache` (bool): Use cached value if available
- `update_cache` (bool): Force cache update

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
print(result)  # Newline-separated list of trigger tests
```

### Available Properties

**CatenaD4J Properties:**
- `classes.modified`: Classes modified by the bug fix
- `tests.trigger`: Trigger tests that expose the bug

**Static Defects4J Properties:**
- `classes.relevant`: Classes loaded by triggering tests
- `dir.src.classes`: Source directory of classes
- `dir.src.tests`: Source directory of tests
- `tests.relevant`: Relevant tests touching modified sources

**Dynamic Defects4J Properties:**
- `cp.compile`: Classpath to compile the project
- `cp.test`: Classpath to run tests
- `dir.bin.classes`: Target directory of classes
- `dir.bin.tests`: Target directory of test classes
- `tests.all`: All developer-written tests

### Helper Functions

```python
def query_c4j(prop: str, proj: str, bid: str, cid: str, wd: str, 
              context: ExecutionContext = None, vtag: str = None) -> str
```
Query CatenaD4J-specific properties.

```python
def query_d4j_static(prop: str, proj: str, bid: str, wd: str,
                     context: ExecutionContext = None, vtag: str = None) -> str
```
Query static Defects4J properties (no build required).

```python
def query_d4j_dynamic(prop: str, proj: str, wd: str,
                      context: ExecutionContext = None) -> str
```
Query dynamic Defects4J properties (requires build processing).

**Example:**
```python
from catena4j.commands.export import query_c4j

# Get trigger tests for a specific bug
tests = query_c4j('tests.trigger', 'Chart', '15', '1', './buggy', context)
```

## xids

List available IDs (project IDs, bug IDs, catena IDs).

**Module:** `catena4j.commands.xids`

### Functions

#### `run_pids(context: ExecutionContext) -> list`

Get all available project IDs.

**Returns:** List of project names (strings)

**Example:**
```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import xids

context = ExecutionContext()
projects = xids.run_pids(context)
print(projects)  # ['Chart', 'Cli', 'Closure', ...]
```

#### `run_bids(context: ExecutionContext) -> list`

Get all bug IDs for a project.

**Arguments (via context.args):**
- `p` (str): Project name

**Returns:** List of bug IDs (integers)

**Example:**
```python
context.args = Namespace(p='Chart')
bugs = xids.run_bids(context)
print(bugs)  # [1, 2, 3, ...]
```

#### `run_cids(context: ExecutionContext) -> list`

Get all catena IDs for a specific bug.

**Arguments (via context.args):**
- `p` (str): Project name
- `b` (str): Bug ID

**Returns:** List of catena IDs (integers)

**Example:**
```python
context.args = Namespace(p='Chart', b='15')
catenas = xids.run_cids(context)
print(catenas)  # [1, 2, 3]
```

## Complete Example: Batch Processing

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import xids, checkout, export
from argparse import Namespace
from pathlib import Path

# Initialize context
context = ExecutionContext()

# Get all projects
projects = xids.run_pids(context)

for project in projects[:2]:  # Process first 2 projects
    print(f"Processing {project}...")
    
    # Get bugs for project
    context.args = Namespace(p=project)
    bugs = xids.run_bids(context)
    
    for bug in bugs[:1]:  # Process first bug
        # Get catena IDs
        context.args = Namespace(p=project, b=str(bug))
        cids = xids.run_cids(context)
        
        for cid in cids:
            version_id = f"{bug}b{cid}"
            work_dir = f"/tmp/{project}_{bug}_{cid}"
            
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
                print(f"  {prop}: {len(result.split())} items")
```

## Error Handling

### Exception: `Catena4JError`

Base exception for CatenaD4J-specific errors.

```python
from catena4j.exceptions import Catena4JError

try:
    checkout.run(context)
except Catena4JError as e:
    print(f"Error: {e}")
```

### Common Error Scenarios

1. **Invalid version ID**: Raised when version format is incorrect
2. **Missing working directory**: When directory doesn't exist for export
3. **Unknown property**: When requesting non-existent property
4. **Loader not found**: When project loader is unavailable

## Best Practices

1. **Always initialize context**: Create proper ExecutionContext with required attributes
2. **Use cache when appropriate**: Enable caching for expensive operations
3. **Handle exceptions**: Wrap API calls in try-except blocks
4. **Validate inputs**: Check version IDs and property names before use
5. **Clean up resources**: Remove temporary working directories after use

## See Also

- [Loaders API](loaders.md) - Project-specific loading and customization
- [Utilities API](utilities.md) - Helper functions for file I/O, git, caching
- [Main README](../../README.md) - Command-line usage examples
