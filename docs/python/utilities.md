# Python Utilities API

This document covers utility functions and helpers in CatenaD4J's Python API.

## Overview

CatenaD4J provides utilities for file I/O, git operations, caching, and Defects4J integration.

## catena4j.util

General utility functions for file operations and process execution.

### File Operations

```python
def read_file(file: Path, encoding: str = None) -> str
```
Read a file with automatic encoding detection.

**Parameters:**
- `file`: Path to file
- `encoding`: Optional specific encoding to use

**Returns:** File contents as string or None if file doesn't exist

**Example:**
```python
from pathlib import Path
from catena4j.util import read_file

content = read_file(Path('/tmp/myfile.txt'))
print(content)
```

```python
def write_file(file: Path, content: str, encoding: str = None)
```
Write content to a file with automatic encoding handling.

**Parameters:**
- `file`: Path to file
- `content`: String content to write
- `encoding`: Optional specific encoding

**Example:**
```python
from catena4j.util import write_file

write_file(Path('/tmp/output.txt'), "Hello, World!")
```

```python
def append_file(file: Path, content: str, encoding: str = None)
```
Append content to a file.

### Property Files

```python
def read_properties(file: Path) -> dict
```
Read a Java-style properties file.

**Returns:** Dictionary of property key-value pairs

```python
def write_properties(file: Path, properties: dict)
```
Write properties to a file in Java format.

**Example:**
```python
from catena4j.util import read_properties, write_properties

# Read properties
props = read_properties(Path('project.properties'))
print(props['version'])

# Write properties
new_props = {'version': '1.0', 'author': 'CatenaD4J'}
write_properties(Path('output.properties'), new_props)
```

### Git Operations

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

**Example:**
```python
from pathlib import Path
from catena4j.util import Git

# Clone repository
Git.clone('https://github.com/example/repo.git', Path('/tmp/repo'))

# Checkout a branch
Git.checkout('develop', Path('/tmp/repo'))

# Apply patch
Git.apply_patch(Path('/patches/fix.patch'), Path('/tmp/repo'))

# Create tag
Git.create_tag('v1.0', Path('/tmp/repo'))
```

### Cache Management

```python
def get_cache_path(context: Namespace, *parts) -> Path
```
Get the path to a cache file.

**Parameters:**
- `context`: Execution context or namespace
- `*parts`: Path components

**Returns:** Path object

**Example:**
```python
from catena4j.util import get_cache_path

cache_path = get_cache_path(context, 'export', 'Chart', '15', 'tests.trigger')
# Returns: <cache_dir>/export/Chart/15/tests.trigger
```

```python
def search_cache(cache: Path, check: Callable = None, 
                fix: Tuple = None, args=(), kwargs={})
```
Search for a value in cache or compute and store it.

## catena4j.c4jutil

CatenaD4J-specific utility functions.

### Version Parsing

```python
def parse_vid(vid: str) -> dict
```
Parse a version ID string into components.

**Parameters:**
- `vid`: Version ID string (e.g., '15b1')

**Returns:** Dictionary with keys:
- `bid`: Bug ID (string)
- `tag`: 'b' or 'f' (buggy/fixed)
- `cid`: Catena ID (string)

**Example:**
```python
from catena4j.c4jutil import parse_vid

info = parse_vid('15b1')
print(info)  # {'bid': '15', 'tag': 'b', 'cid': '1'}
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

### Git Operations

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

### Constants

```python
BUGGY = 'b'
FIXED = 'f'
ERR = -1
```

**Example:**
```python
from catena4j.c4jutil import BUGGY, FIXED, check_vid, parse_vid

# Validate version ID
if check_vid('15b1'):
    info = parse_vid('15b1')
    if info['tag'] == BUGGY:
        print("This is a buggy version")
```

## catena4j.d4jutil

Defects4J integration utilities.

### Bug Information

```python
def get_classes_modified(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of modified classes for a bug.

**Returns:** List of fully-qualified class names

```python
def get_tests_trigger(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of trigger tests for a bug.

**Returns:** List of test method names

```python
def get_classes_relevant(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of relevant classes for a bug.

```python
def get_tests_relevant(proj: str, bid: str, context: ExecutionContext) -> list
```
Get list of relevant tests for a bug.

**Example:**
```python
from catena4j.d4jutil import get_classes_modified, get_tests_trigger

# Get modified classes
classes = get_classes_modified('Chart', '15', context)
print(f"Modified classes: {classes}")

# Get trigger tests
tests = get_tests_trigger('Chart', '15', context)
print(f"Trigger tests: {tests}")
```

### Directory Information

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

### Patch Operations

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

## Complete Example

```python
from pathlib import Path
from catena4j.dispatcher import ExecutionContext
from catena4j.util import read_file, write_file, get_cache_path, Git
from catena4j.c4jutil import parse_vid, check_vid, init_git_repository
from catena4j.d4jutil import get_classes_modified, get_tests_trigger

# Initialize context
context = ExecutionContext()

# Parse and validate version ID
vid = '15b1'
if check_vid(vid):
    info = parse_vid(vid)
    print(f"Bug: {info['bid']}, Type: {info['tag']}, Catena: {info['cid']}")

# Get bug information
classes = get_classes_modified('Chart', '15', context)
tests = get_tests_trigger('Chart', '15', context)

# Write to cache
cache_path = get_cache_path(context, 'analysis', 'Chart', '15')
write_file(cache_path / 'classes.txt', '\n'.join(classes))
write_file(cache_path / 'tests.txt', '\n'.join(tests))

# Read from cache
cached_classes = read_file(cache_path / 'classes.txt')
print(f"Cached classes:\n{cached_classes}")

# Git operations
work_dir = Path('/tmp/chart15')
init_git_repository(work_dir)
Git.checkout('main', work_dir)
```

## Best Practices

1. **Use Path objects**: Prefer pathlib.Path over string paths
2. **Handle encoding**: Let utilities handle encoding automatically
3. **Cache expensive operations**: Use cache utilities for repeated queries
4. **Check existence**: Use read_file's None return to check file existence
5. **Clean up**: Remove temporary files and directories

## See Also

- [Commands API](commands.md) - Commands that use these utilities
- [Loaders API](loaders.md) - Loaders that use these utilities
- [Main README](../../README.md) - Overview and usage
