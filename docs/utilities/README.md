# Utilities Guide

## Overview

CatenaD4J provides three utility modules:
- **`util.py`**: General-purpose utilities (I/O, VCS, caching, task printing)
- **`c4jutil.py`**: CatenaD4J-specific operations
- **`d4jutil.py`**: Defects4J integration utilities

## General Utilities (`util.py`)

### File I/O

#### Reading and Writing Files

```python
from catena4j.util import read_file, write_file, append_file
from pathlib import Path

# Read file with automatic encoding detection
content = read_file(Path('file.txt'))  # Returns None if not exists

# Write file (creates parent directories if needed)
write_file(Path('output.txt'), 'content')

# Append to file
append_file(Path('log.txt'), 'new line\n')
```

**Encoding Handling**:
- Tries UTF-8 first, then Latin-1
- Custom encoding: `read_file(path, encoding='utf-16')`
- Set global encodings: `set_encodings(('utf-8', 'iso-8859-1'))`

#### Properties Files

```python
from catena4j.util import read_properties, write_properties

# Read Java properties file
props = read_properties(Path('build.properties'))
# Returns: {'key1': 'value1', 'key2': 'value2', ...}

# Write properties
write_properties(Path('build.properties'), {
    'project.name': 'MyProject',
    'version': '1.0.0'
})
```

### Caching

#### Cache Path Management

```python
from catena4j.util import get_cache_path, search_cache
from catena4j.env import get_system_context

context = get_system_context()

# Get cache file path
cache_path = get_cache_path(context, 'component', 'subdir', 'file.txt')
# Returns: <c4j_home>/.cache/component/subdir/file.txt
```

#### Smart Caching

```python
from catena4j.util import search_cache

def expensive_computation():
    # Time-consuming operation
    return "result"

# Search cache or compute and store
result = search_cache(
    cache=cache_path,
    check=lambda content: len(content) > 0,  # Validation function
    fix=expensive_computation,  # Computation function if cache miss
    args=(),  # Arguments for fix function
    kwargs={}
)
```

### Version Control Systems

#### Git Operations

```python
from catena4j.util import Git
from catena4j.loaders import get_project_loader

# Git is typically used through loaders
LoaderClass = get_project_loader('Math')
loader = LoaderClass(context)

# Git instance is created automatically
git = loader.version_control_system

# Checkout revision
git.checkout_revision('abc123', './work')

# Export diff
diff = git.export_diff('commit1', 'commit2')
write_file(Path('patch.diff'), diff)

# Format repository name
repo_name = Git.format_name('myproject')  # Returns: 'myproject.git'
```

#### SVN Operations

```python
from catena4j.util import Svn

# Similar API to Git
svn = Svn(loader)
svn.checkout_revision('r12345', './work')
diff = svn.export_diff('r12345', 'r12346')
```

### Task Printing

Progress feedback for long-running operations.

```python
from catena4j.util import TaskPrinter, get_auto_task_printer

# Manual usage
with TaskPrinter("Compiling project") as printer:
    compile_project()  # Long operation
# Prints: "Compiling project.................... DONE"
# Or:     "Compiling project.................... FAILED" (on exception)

# Verbose mode
with TaskPrinter("Building") as printer:
    printer.verbose = True
    # Additional messages will be shown

# Automatic mode (context-aware)
printer = get_auto_task_printer(context)  # None if not in CLI mode
if printer:
    with printer("Processing"):
        process()

# Function wrapper
from catena4j.util import auto_task_print

result = auto_task_print("Task name", function, args=(arg1, arg2))
```

**Configuration**:
```python
TaskPrinter.configurate(
    start='⏳ RUNNING',  # Start indicator
    done='✅ DONE',      # Success indicator  
    fail='❌ FAILED',    # Failure indicator
    anchor=75,          # Message column width
    padding='.'         # Padding character
)
```

### Command Execution

#### Running Shell Commands

```python
from catena4j.util import run_command, run_command_task

# Basic execution
success, stdout, stderr = run_command(
    cmd=['ls', '-la'],
    cwd='/path/to/dir',
    timeout=30,  # seconds
    env=custom_env  # optional environment
)

if success:
    output = stdout.decode('utf-8')
    print(output)

# With task printer
run_command_task(
    cmd=['make', 'all'],
    wd='/project',
    task_printer=TaskPrinter("Building"),
    env=custom_env
)
```

#### Toolkit Execution

```python
from catena4j.util import toolkit_execute

# Execute Java toolkit
result = toolkit_execute(
    target='tests.all',  # Property or target
    project='Chart',
    wd='./workspace',
    xml_attr='c4j_rel_project_export_xml',  # Config attribute for XML path
    main_attr='c4j_toolkit_export_main',  # Config attribute for main class
    context=context,
    task_printer=None,  # Optional task printer
    java_options=['-Xmx2g']  # Optional JVM options
)
```

### Helper Functions

```python
from catena4j.util import (
    find_path,          # Find executable in PATH
    get_constant_class, # Create immutable class
    build_args,         # Create Namespace
    noreturn,           # Call function and exit
    do_nothing          # No-op function
)

# Find path to executable
d4j_home = find_path('defects4j', parent_level=2)

# Create immutable configuration object
Config = get_constant_class('Config', {'key': 'value'})
config = Config()
# config.key = 'new'  # Raises AttributeError

# Build arguments namespace
args = build_args(project='Chart', bug_id='15')

# Execute and exit
noreturn(main_function, arg1, arg2)

# Placeholder function
hook = custom_hook if has_hook else do_nothing
hook()  # Safe to call
```

## CatenaD4J Utilities (`c4jutil.py`)

CatenaD4J-specific operations and helpers.

### Version Information

```python
from catena4j.c4jutil import (
    parse_vid,
    check_vid,
    read_version_info,
    get_tag_name_from_ver
)

# Parse version ID string
bid, tag, cid = parse_vid('15b1')
# Returns: ('15', 'b', '1')

bid, tag, cid = parse_vid('20f3')
# Returns: ('20', 'f', '3')

# Validate version ID format
is_valid = check_vid('15b1')  # True
is_valid = check_vid('invalid')  # False

# Read version info from working directory
version_info = read_version_info('./workspace', context)
# Returns: {
#     'pid': 'Chart',
#     'bid': '15',
#     'cid': '1',
#     'tag': 'b'
# }

# Get git tag name
tag_name = get_tag_name_from_ver('Chart', '15', '1', 'b')
# Returns: 'C4J_Chart_15_1_buggy'
```

### Property Access

```python
from catena4j.c4jutil import get_property

# Get CatenaD4J property
tests_trigger = get_property(
    'tests.trigger',
    project='Chart',
    bid='15',
    cid='1',
    context=context
)

# Get patch data
test_patch = get_property('test.patch', 'Chart', '15', '1', context)
src_patch = get_property('src.patch', 'Chart', '15', '1', context)
```

### Bug Registry

```python
from catena4j.c4jutil import get_bugs_registry

# Get all bugs for a project
bugs = get_bugs_registry('Chart', context)
# Returns: {
#     '15': {'1', '2', '3'},  # Bug 15 has CIDs 1, 2, 3
#     '20': {'1'},
#     ...
# }

# Check if bug/cid exists
if '15' in bugs and '1' in bugs['15']:
    print("Bug Chart-15 CID 1 exists")
```

### Working Directory Operations

```python
from catena4j.c4jutil import (
    check_working_directory,
    is_protected_directory,
    init_git_repository,
    create_commit_and_tag
)

# Check if directory is a valid CatenaD4J working directory
is_valid, version_info = check_working_directory('./workspace', context)

# Prevent operations on protected directories
if is_protected_directory('./workspace'):
    raise Error("Cannot modify protected directory")

# Initialize git repository
repo = init_git_repository('./workspace')

# Create commit and tag
create_commit_and_tag(
    wd='./workspace',
    tag='C4J_Chart_15_1_buggy',
    message='Checkout buggy version',
    context=context
)
```

### Patch Operations

```python
from catena4j.c4jutil import apply_json_patch
from catena4j.util import Files
import json

# Load patch
patch_data = json.loads(get_property('test.patch', 'Chart', '15', '1', context))

# Apply patches
files = Files('./workspace')
for hunk_id in patch_data:
    apply_json_patch(patch_data[hunk_id], files)
```

## Defects4J Utilities (`d4jutil.py`)

Integration with Defects4J infrastructure.

### Bug Information

```python
from catena4j.d4jutil import (
    get_active_bugs,
    get_deprecated_bugs,
    get_revision_id,
    get_src_patch_dir
)

# Get active bugs
active_bugs = get_active_bugs('Chart', context)
# Returns: {
#     '1': {'revision.id.buggy': 'r1', 'revision.id.fixed': 'r2', ...},
#     '2': {...},
#     ...
# }

# Get deprecated bugs
deprecated = get_deprecated_bugs('Chart', context)

# Get revision ID for a bug
revision_id = get_revision_id('Chart', '15', buggy=True, context=context)

# Get patch directory
patch_dir = get_src_patch_dir('Chart', '15', context)
```

### Properties Export

```python
from catena4j.d4jutil import (
    get_classes_modified,
    get_classes_relevant,
    get_tests_trigger,
    get_tests_relevant,
    get_dir_src_classes,
    get_dir_src_tests
)

# Get modified classes
classes = get_classes_modified('Chart', '15', context)
# Returns: ['org.jfree.chart.ChartPanel', ...]

# Get relevant classes (loaded by tests)
classes = get_classes_relevant('Chart', '15', context)

# Get trigger tests
tests = get_tests_trigger('Chart', '15', context)
# Returns: ['org.jfree.chart.ChartPanelTest::testMethod', ...]

# Get relevant tests
tests = get_tests_relevant('Chart', '15', context)

# Get source directories
src_dir = get_dir_src_classes('Chart', '15', buggy=True, context=context)
test_dir = get_dir_src_tests('Chart', '15', buggy=True, context=context)
```

### Property Filling

```python
from catena4j.d4jutil import fill_properties

# Fill Defects4J properties in working directory
fill_properties(
    project='Chart',
    bid='15',
    wd='./workspace',
    is_buggy=True,
    context=context
)
```

### Test Fixing

```python
from catena4j.d4jutil import fix_tests

# Fix test formatting (Defects4J to JUnit format)
fix_tests(
    project='Chart',
    bid='15',
    wd='./workspace',
    context=context
)
```

## Best Practices

### File I/O

✅ **Use encoding-aware functions**:
```python
# Good
from catena4j.util import read_file, write_file
content = read_file(path)

# Avoid
with open(path) as f:  # May fail on non-UTF-8 files
    content = f.read()
```

✅ **Check for file existence**:
```python
content = read_file(path)
if content is not None:
    process(content)
```

### Caching

✅ **Use search_cache for expensive operations**:
```python
result = search_cache(
    cache=cache_path,
    check=validation_function,
    fix=computation_function
)
```

✅ **Invalidate cache when needed**:
```python
if args.update_cache:
    # Recompute even if cache exists
    result = compute()
    write_file(cache_path, result)
```

### Task Printing

✅ **Use in CLI mode only**:
```python
printer = None
if context.mode == ExecutionContext.CLI:
    printer = TaskPrinter("Task")

if printer:
    with printer:
        work()
else:
    work()
```

✅ **Use auto_task_print for simple cases**:
```python
result = auto_task_print("Task", function, (arg1, arg2))
```

### Command Execution

✅ **Handle errors appropriately**:
```python
success, stdout, stderr = run_command(cmd, cwd=wd)
if not success:
    error_msg = stderr.decode('utf-8')
    raise Catena4JError(f"Command failed: {error_msg}")
```

✅ **Use timeouts for potentially hanging commands**:
```python
run_command(cmd, timeout=300)  # 5 minutes
```

## Examples

### Example 1: Custom Property Export

```python
from catena4j.util import get_cache_path, read_file, write_file
from catena4j.c4jutil import read_version_info

def export_custom_property(wd, context):
    # Read version info
    version_info = read_version_info(wd, context)
    
    # Check cache
    cache_path = get_cache_path(context, 'custom', 
                                version_info['pid'],
                                version_info['bid'],
                                'property.txt')
    
    cached = read_file(cache_path)
    if cached:
        return cached
    
    # Compute property
    result = compute_property(version_info)
    
    # Cache result
    write_file(cache_path, result)
    
    return result
```

### Example 2: Batch Processing

```python
from catena4j.c4jutil import get_bugs_registry
from catena4j.util import TaskPrinter

def process_all_bugs(project, context):
    bugs = get_bugs_registry(project, context)
    
    total = sum(len(cids) for cids in bugs.values())
    count = 0
    
    for bid, cids in bugs.items():
        for cid in cids:
            count += 1
            with TaskPrinter(f"Processing {project}-{bid}-{cid} ({count}/{total})"):
                process_bug(project, bid, cid)
```

### Example 3: Diff Analysis

```python
from catena4j.util import Git
from catena4j.loaders import get_project_loader
from pathlib import Path

def analyze_changes(project, bid, context):
    # Get loader
    LoaderClass = get_project_loader(project)
    loader = LoaderClass(context)
    
    # Get revision IDs
    buggy_rev = get_revision_id(project, bid, buggy=True, context=context)
    fixed_rev = get_revision_id(project, bid, buggy=False, context=context)
    
    # Export diff
    diff_path = Path(f'/tmp/{project}_{bid}.diff')
    diff = loader.export_diff(buggy_rev, fixed_rev, diff_path)
    
    # Analyze diff
    lines_changed = len(diff.split('\n'))
    files_changed = diff.count('diff --git')
    
    return {
        'lines': lines_changed,
        'files': files_changed,
        'diff_path': diff_path
    }
```

## See Also

- [API Reference](../API.md) - Complete API documentation
- [Commands Guide](../commands/README.md) - Using utilities in commands
- [Loaders Guide](../loaders/README.md) - Using utilities in loaders
