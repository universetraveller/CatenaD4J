# Commands Guide

## Overview

Commands are the primary way users interact with CatenaD4J. This guide covers command implementation, registration, and extension.

## Command Architecture

### Command Structure

```
Command Module (e.g., checkout.py)
├── initialize()         # Create CLI parser
├── run(context)        # Main command logic
└── Helper functions    # Supporting logic
```

### Command Lifecycle

```
1. Bootstrap Phase
   - initialize() called
   - Creates argument parser
   - Defines CLI options
         ↓
2. Registration
   - Command registered with entry point
   - Added to command registry
         ↓
3. Execution
   - User invokes command
   - Arguments parsed
   - ExecutionContext created
   - run(context) called
         ↓
4. Result Handling
   - CLI mode: print to stdout/stderr
   - API mode: return result
```

## Built-in Commands

### checkout

Check out a specific bug version to a working directory.

**Module**: `catena4j/commands/checkout.py`

**Key Functions**:

#### `initialize()`
Creates CLI parser with arguments:
- `-p`: Project ID (required)
- `-v`: Version ID in format `<bid><b/f><cid>` (required)
- `-w`: Working directory path (required)
- `--full-history`: Generate additional commit history

#### `run(context: ExecutionContext)`
Main implementation:
1. Parse version ID into bid, tag, cid
2. Validate project and bug exist
3. Check/create working directory
4. Delegate to `d4j_checkout_vid()` for Defects4J checkout
5. Apply CatenaD4J-specific patches
6. Create git commits and tags

#### `d4j_checkout_vid(project, bid, tag, wd, context, loader=None)`
Core checkout logic:
- Checkout Defects4J revision
- Run project-specific hooks
- Apply test modifications
- Apply bug-specific hunks
- Create version control tags

**Extension Points**:
- `loader.d4j_checkout_hook()`: Project-specific post-checkout operations
- `loader.load_buggy_version()`: Apply buggy version patches
- `loader.load_fixed_version()`: Apply fixed version patches

### export

Export version-specific properties of a checked-out bug.

**Module**: `catena4j/commands/export.py`

**Key Functions**:

#### `initialize()`
Creates CLI parser with arguments:
- `-p`: Property name (required)
- `-w`: Working directory (optional)
- `-o`: Output file path (optional, default: stdout)
- `--from-cache`: Use cached results
- `--update-cache`: Force cache refresh

#### `run(context: ExecutionContext)`
Main implementation:
1. Read version info from working directory
2. Check cache if requested
3. Determine property type (C4J, D4J static, D4J dynamic)
4. Query appropriate source
5. Update cache if needed
6. Output result

#### `query_c4j(prop, proj, bid, cid, wd, context, vtag)`
Query CatenaD4J properties:
- `classes.modified`
- `tests.trigger`

Reads from project metadata in `projects/<project>/patches/`.

#### `query_d4j_static(prop, proj, bid, wd, context, vtag)`
Query Defects4J static properties:
- `classes.relevant`
- `dir.src.classes`
- `dir.src.tests`
- `tests.relevant`

Reads from Defects4J repository metadata.

#### `query_d4j_dynamic(prop, proj, wd, context)`
Query Defects4J dynamic properties:
- `cp.compile`
- `cp.test`
- `dir.bin.classes`
- `dir.bin.tests`
- `tests.all`

Executes Java toolkit to compute values.

**Caching**:
```
Cache Path: .cache/export/<pid>/<bid>/<cid?>/<property>

# With cache hit:
read_file(cache_path) → return result

# With cache miss:
compute_property() → write_file(cache_path) → return result
```

### test

Run tests on a checked-out project version.

**Module**: `catena4j/commands/test.py`

**Key Functions**:

#### `initialize()`
Creates CLI parser with arguments:
- `-w`: Working directory (optional)
- `-c, --compile`: Compile before testing
- `-l, --list`: List tests without running
- `-i, --isolation`: Isolation level (1, 2, or 3)
- `-t`: Specific test(s) to run (repeatable)
- `-r`: Run relevant tests only
- `--trigger`: Run trigger tests only
- `-a`: Collect all failed assertions (experimental)

#### `run(context: ExecutionContext)`
Main implementation:
1. Read version info
2. Compile if requested
3. Determine test set (specific, relevant, trigger, or all)
4. Call `run_tests()`

#### `run_tests(tests, project, wd, context, list_only, assertions, isolation, test_name)`
Execute tests via Java toolkit:
1. Get project loader
2. Configure Java options
3. Set isolation level
4. Execute via `loader.toolkit_execute()`
5. Capture and return results

**Isolation Levels**:
- **Level 1**: Reused isolated classloader (fastest)
  - Uses `JUnit4Helper`
  - Single classloader for all tests
  - Best for quick test runs
  
- **Level 2**: Per-class isolated classloader
  - Uses `JUnit4Helper1`
  - New classloader for each test class
  - Better isolation, slight performance cost
  
- **Level 3**: Ant's JUnit task (slowest, most isolated)
  - Uses standard Ant JUnit runner
  - Maximum isolation
  - Highest overhead

**Test Output**:
- **List mode**: Writes all tests to `<work_dir>/all_tests`
- **Execution mode**: Writes failing tests to `<work_dir>/failing_tests`

### compile

Compile a checked-out project version.

**Module**: `catena4j/commands/compile.py`

**Key Functions**:

#### `initialize()`
Creates CLI parser with arguments:
- `-w`: Working directory (optional)
- `--target`: Compilation target (default: `compile.tests`)
- `--verbose`: Show detailed output

#### `run(context: ExecutionContext)`
Main implementation:
1. Validate target (must contain 'compile' or be 'clean')
2. Read version info
3. Call `execute_compile()`

#### `execute_compile(target, proj, wd, context, task_printer)`
Execute compilation:
1. Get project loader
2. Call `loader.toolkit_execute()` with target
3. Display progress if in CLI mode

**Valid Targets**:
- `compile`: Compile source classes only
- `compile.tests`: Compile source and test classes (default)
- `clean`: Clean build artifacts
- Custom targets containing 'compile'

**Security Note**: Target validation prevents arbitrary Ant target execution.

### clean

Clean build output directory.

**Module**: `catena4j/commands/compile.py`

**Key Functions**:

#### `clean(context: ExecutionContext)`
Wrapper that sets target to 'clean' and calls `compile.run()`.

### reset

Reset unstaged modifications in a working directory.

**Module**: `catena4j/commands/checkout.py`

**Key Functions**:

#### `reset(context: ExecutionContext)`
1. Determine working directory
2. Verify it's a valid CatenaD4J/Defects4J directory
3. Reset using git: `git reset --hard HEAD`

**Safety**: Only operates on recognized working directories.

### pids, bids, cids

Query available project IDs, bug IDs, and catena IDs.

**Module**: `catena4j/commands/xids.py`

**Key Functions**:

#### `query_pids(context)`
List all projects:
1. Scan `projects/` directory
2. Return sorted list of project names
3. Cache results in context

#### `query_bids(project, context)`
List bug IDs for a project:
1. Read from `active-bugs.csv` or `bugs-registry.csv`
2. Filter by options (-D for deprecated, -A for all)
3. Return sorted list

#### `query_cids(project, id, context)`
List catena IDs for a bug:
1. Read `bugs-registry.csv`
2. Extract CIDs for specified bug
3. Return sorted list

**Caching Strategy**:
- Project IDs cached in `context.c4j_cache`
- Bug metadata cached per-project
- CID lookups read from cached bug registry

## Creating Custom Commands

### Step-by-Step Guide

#### 1. Create Command Module

Create `catena4j/commands/mycommand.py`:

```python
from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext
from ..util import TaskPrinter, print_result

_parser = None

def initialize():
    """Initialize CLI parser for this command"""
    global _parser
    _parser = _create_command(
        'mycommand',
        help='Short description for command list',
        description='Detailed description shown in help text',
        add_help=False  # Disable default help to customize
    )
    
    # Add required arguments
    _parser.add_argument('-p', required=True, 
                         metavar='parameter',
                         help='Parameter description')
    
    # Add optional arguments
    _parser.add_argument('--option', 
                         required=False,
                         default='default_value',
                         help='Optional parameter')
    
    # Add flags
    _parser.add_argument('--verbose', 
                         action='store_true',
                         help='Enable verbose output')
    
    # Enable argument help in -h output
    _parser.__add_arguments_help__ = True

def run(context: ExecutionContext):
    """
    Main command implementation
    
    Args:
        context: Execution context with args, mode, and system context
        
    Returns:
        Result value (any type, typically str or list)
    """
    args = context.args
    
    # Create task printer for CLI feedback
    printer = None
    if context.mode == ExecutionContext.CLI:
        printer = TaskPrinter("Processing...")
    
    try:
        # Access arguments
        param = args.p
        option = args.option
        verbose = args.verbose
        
        # Access system context
        c4j_home = context.c4j_home
        d4j_home = context.d4j_home
        
        # Command logic here
        with printer if printer else lambda: None:
            result = process_command(param, option, verbose)
        
        # Handle output based on mode
        if context.mode == ExecutionContext.CLI:
            print_result(result)
        
        return result
        
    except Exception as e:
        if printer:
            printer.__exit__(type(e), e, None)
        raise

# Helper functions
def process_command(param, option, verbose):
    """Command-specific logic"""
    # Implementation
    return f"Processed {param} with {option}"
```

#### 2. Register Command

Edit `catena4j/bootstrap.py`:

```python
def initialize_commands():
    '''Default implementation of commands initialization'''
    from .commands import (
        # ... existing imports ...
        mycommand  # Add import
    )
    
    # ... existing initializations ...
    
    # Add initialization
    mycommand.initialize()
    _register('mycommand', mycommand.run)
```

#### 3. Use Command

```bash
# CLI usage
catena4j mycommand -p value --option custom --verbose

# Programmatic usage
from catena4j.dispatcher import CommandDispatcher
from argparse import Namespace

dispatcher = CommandDispatcher()
args = Namespace(p='value', option='custom', verbose=True)
result = dispatcher.run('mycommand', args, cli=False)
```

### Best Practices

#### DO

✅ **Validate Arguments Early**:
```python
def run(context):
    args = context.args
    if not valid_input(args.p):
        raise Catena4JError(f"Invalid input: {args.p}")
```

✅ **Respect Execution Mode**:
```python
def run(context):
    result = compute_result()
    
    if context.mode == ExecutionContext.CLI:
        print_result(result)  # Print to stdout
    
    return result  # Always return for API mode
```

✅ **Use Task Printers for Long Operations**:
```python
with TaskPrinter("Long operation") as printer:
    # Time-consuming work
    result = long_operation()
# Automatically prints "DONE" or "FAILED"
```

✅ **Leverage Context Attributes**:
```python
def run(context):
    # Access system paths
    projects_dir = Path(context.c4j_home, context.c4j_rel_projects)
    
    # Access configuration
    isolation_level = context.c4j_test_isolation_level
    
    # Modify context for subcommands
    new_context = context.copy()
    new_context.custom_setting = 'value'
```

✅ **Cache Expensive Operations**:
```python
from ..util import get_cache_path, read_file, write_file

def run(context):
    cache_path = get_cache_path(context, 'mycommand', 'result')
    
    cached = read_file(cache_path)
    if cached:
        return cached
    
    result = expensive_computation()
    write_file(cache_path, result)
    return result
```

#### DON'T

❌ **Don't Print in API Mode**:
```python
# Bad
def run(context):
    print("Processing...")  # Always prints
    return result

# Good
def run(context):
    if context.mode == ExecutionContext.CLI:
        print("Processing...")
    return result
```

❌ **Don't Modify System Context**:
```python
# Bad
def run(context):
    context.c4j_home = '/new/path'  # Won't work, read-only
```

❌ **Don't Catch All Exceptions Silently**:
```python
# Bad
def run(context):
    try:
        risky_operation()
    except:
        pass  # Hides errors

# Good
def run(context):
    try:
        risky_operation()
    except SpecificError as e:
        logger.error(f"Operation failed: {e}")
        raise
```

❌ **Don't Forget to Initialize Parser**:
```python
# Bad - Missing initialize()
def run(context):
    # No way to get arguments
```

❌ **Don't Use Global State**:
```python
# Bad
global_result = None

def run(context):
    global global_result
    global_result = compute()
```

## Advanced Patterns

### Subcommands with Shared Logic

```python
# commands/database.py

def initialize():
    # Create separate parsers for subcommands
    _create = _create_command('db-create', help='Create database')
    _create.add_argument('-n', required=True, metavar='name')
    
    _delete = _create_command('db-delete', help='Delete database')
    _delete.add_argument('-n', required=True, metavar='name')

def run_create(context):
    db_operation('create', context.args.n)

def run_delete(context):
    db_operation('delete', context.args.n)

def db_operation(op, name):
    """Shared logic"""
    # Common implementation
    pass

# Register both
# bootstrap.py: _register('db-create', database.run_create)
# bootstrap.py: _register('db-delete', database.run_delete)
```

### Progressive Enhancement

```python
def run(context):
    """Command with optional features"""
    args = context.args
    
    # Basic functionality always available
    result = basic_operation(args.input)
    
    # Enhanced functionality if available
    if has_feature('advanced'):
        result = enhance(result)
    
    # Optional post-processing
    if args.optimize:
        result = optimize(result)
    
    return result
```

### Delegation to Loaders

```python
from ..loaders import get_project_loader

def run(context):
    """Delegate project-specific work to loader"""
    args = context.args
    project = args.p
    
    # Get appropriate loader
    LoaderClass = get_project_loader(project)
    loader = LoaderClass(context)
    
    # Delegate operation
    result = loader.custom_operation(args.parameter)
    
    return result
```

### Multi-Stage Workflows

```python
def run(context):
    """Command with multiple stages"""
    args = context.args
    
    # Stage 1: Validation
    with TaskPrinter("Validating input"):
        validate_inputs(args)
    
    # Stage 2: Preparation
    with TaskPrinter("Preparing environment"):
        setup_environment(context)
    
    # Stage 3: Processing
    with TaskPrinter("Processing data"):
        result = process_data(args)
    
    # Stage 4: Cleanup
    with TaskPrinter("Cleaning up"):
        cleanup()
    
    return result
```

### Error Handling

```python
from ..exceptions import Catena4JError

def run(context):
    """Command with proper error handling"""
    args = context.args
    
    # Validate early
    if not validate(args):
        raise Catena4JError("Invalid arguments")
    
    try:
        result = risky_operation()
    except FileNotFoundError as e:
        raise Catena4JError(f"Required file not found: {e}")
    except subprocess.CalledProcessError as e:
        raise Catena4JError(f"External command failed: {e}")
    
    return result
```

## Testing Commands

### Unit Testing

```python
# tests/test_mycommand.py
import unittest
from argparse import Namespace
from catena4j.dispatcher import CommandDispatcher

class TestMyCommand(unittest.TestCase):
    def setUp(self):
        self.dispatcher = CommandDispatcher()
    
    def test_basic_execution(self):
        args = Namespace(p='value', option='test')
        result = self.dispatcher.run('mycommand', args, cli=False)
        self.assertEqual(result, expected_result)
    
    def test_error_handling(self):
        args = Namespace(p='invalid')
        with self.assertRaises(Catena4JError):
            self.dispatcher.run('mycommand', args, cli=False)
```

### Integration Testing

```bash
#!/bin/bash
# Test command end-to-end

# Setup
mkdir -p test_workspace

# Run command
catena4j mycommand -p test_value --option custom -w test_workspace

# Verify results
if [ -f test_workspace/output.txt ]; then
    echo "PASS: Output file created"
else
    echo "FAIL: Output file missing"
    exit 1
fi

# Cleanup
rm -rf test_workspace
```

## Common Patterns

### Reading Version Info

```python
from ..c4jutil import read_version_info

def run(context):
    wd = context.args.w or context.cwd
    version_info = read_version_info(wd, context)
    
    project = version_info['pid']
    bug_id = version_info['bid']
    catena_id = version_info['cid']
    tag = version_info['tag']  # 'b' or 'f'
```

### Calling Java Toolkit

```python
from ..util import toolkit_execute

def run(context):
    result = toolkit_execute(
        target='custom.task',
        project=args.p,
        wd=args.w,
        xml_attr='c4j_rel_project_export_xml',
        main_attr='c4j_toolkit_execute_main',
        context=context
    )
    return result
```

### Working with Properties

```python
from ..util import read_properties, write_properties
from pathlib import Path

def run(context):
    props_file = Path(context.cwd, 'build.properties')
    
    # Read
    props = read_properties(props_file)
    value = props.get('key', 'default')
    
    # Modify
    props['new_key'] = 'new_value'
    
    # Write
    write_properties(props_file, props)
```

## See Also

- [API Reference](API.md) - Execution context and dispatcher
- [CLI Guide](cli.md) - Argument parsing
- [Loaders Guide](loaders.md) - Delegating to loaders
- [Utilities Guide](utilities.md) - Helper functions
