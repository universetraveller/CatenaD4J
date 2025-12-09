# Loaders Guide

## Overview

Loaders are responsible for project-specific operations in CatenaD4J. Each project can have its own loader to handle unique requirements such as different directory layouts, VCS systems, and post-checkout modifications.

## Loader Architecture

### Hierarchy

```
Loader (base marker interface)
    ↓
ContextAwareLoader (adds execution context)
    ↓
ProjectLoader (abstract base for projects)
    ↓
ConcreteProjectLoader (e.g., ChartLoader, MathLoader)
```

### Responsibilities

Loaders handle:
- **VCS Operations**: Checkout, diff, tag operations
- **Directory Layout**: Determine source and test directories
- **Property Access**: Retrieve CatenaD4J-specific properties
- **Post-Checkout Hooks**: Project-specific modifications
- **Bug Patching**: Apply buggy/fixed version patches
- **Toolkit Execution**: Run Java toolkit operations

## Base Loader Classes

### `Loader` (`loader.py`)

```python
class Loader:
    pass
```

Base marker interface for all loaders. Provides type identification.

### `ContextAwareLoader` (`loader.py`)

```python
class ContextAwareLoader(Loader):
    def __init__(self, context: ExecutionContext):
        self.context = context
```

Base class for loaders that need access to execution context.

**Attributes**:
- `context`: Execution context with system settings and command arguments

**Usage**:
```python
class MyLoader(ContextAwareLoader):
    def __init__(self, context):
        super().__init__(context)
        # Access context
        self.c4j_home = context.c4j_home
```

### `ProjectLoader` (`project_loader.py`)

Abstract base class for project-specific loaders.

**Required Class Attributes**:
```python
class MyProjectLoader(ProjectLoader):
    version_control_system_class = Git  # or Svn
    project_name = 'myproject'  # Project identifier
```

**Properties**:

#### `version_control_system`
```python
@property
def version_control_system(self):
    return self._version_control_system
```
Lazily-initialized VCS instance for this loader.

#### `src_layout`
```python
@property
def src_layout(self):
    return self._layout['src']
```
Source directory layout (computed from `determine_layout()`).

#### `test_layout`
```python
@property
def test_layout(self):
    return self._layout['test']
```
Test directory layout (computed from `determine_layout()`).

#### `repo_path`
```python
@property
def repo_path(self):
    return Path(self.context.d4j_home,
                self.context.d4j_rel_repositories,
                self.rel_to_repo)
```
Path to VCS repository.

**Required Methods**:

#### `determine_layout()`
```python
def determine_layout(self) -> dict:
    """
    Return directory layout for source and test files.
    
    Returns:
        dict: {
            'src': str or list[str],  # Source directory path(s)
            'test': str or list[str]  # Test directory path(s)
        }
    """
    raise NotImplementedError('Must be implemented by subclass')
```

**Optional Methods**:

#### `d4j_checkout_hook(project, revision_id, wd)`
```python
def d4j_checkout_hook(self, project: str, revision_id: str, wd: str) -> bool:
    """
    Project-specific operations after Defects4J checkout.
    
    Args:
        project: Project name
        revision_id: VCS revision identifier
        wd: Working directory path
        
    Returns:
        bool: True if files were modified, False otherwise
    """
    return False
```

Called after VCS checkout to apply project-specific fixes.

**Provided Methods**:

#### `checkout_revision(revision_id, wd)`
```python
def checkout_revision(self, revision_id: str, wd: str):
    """
    Checkout a specific VCS revision.
    
    Delegates to version_control_system.checkout_revision()
    """
    return self.version_control_system.checkout_revision(revision_id, wd)
```

#### `export_diff(a, b, output)`
```python
def export_diff(self, a: str, b: str, output: Path = None) -> str:
    """
    Export diff between two revisions.
    
    Args:
        a: First revision ID
        b: Second revision ID
        output: Optional output file path
        
    Returns:
        str: Diff content
    """
    return self.version_control_system.export_diff(a, b, output)
```

#### `get_property(name, project, bid, cid)`
```python
def get_property(self, name: str, project: str, bid: str, cid: str) -> str:
    """
    Get a CatenaD4J property value.
    
    Delegates to c4jutil.get_property()
    """
    return get_property(name, project, bid, cid, self.context)
```

#### `load_buggy_version(project, bid, cid, wd)`
```python
def load_buggy_version(self, project: str, bid: str, cid: str, wd: str) -> None:
    """
    Apply patches for buggy version.
    
    Reads test patches from metadata and applies them.
    """
    files = Files(wd)
    test_patch = json.loads(self.get_property('test.patch', project, bid, cid))
    for hunk in test_patch:
        apply_json_patch(test_patch[hunk], files)
```

#### `load_fixed_version(project, bid, cid, wd)`
```python
def load_fixed_version(self, project: str, bid: str, cid: str, wd: str) -> None:
    """
    Apply patches for fixed version.
    
    Reads test and source patches from metadata and applies them.
    """
    files = Files(wd)
    
    # Apply test patches
    test_patch = json.loads(self.get_property('test.patch', project, bid, cid))
    for hunk in test_patch:
        apply_json_patch(test_patch[hunk], files)
    
    # Apply source patches
    src_patch = json.loads(self.get_property('src.patch', project, bid, cid))
    for hunk in src_patch:
        apply_json_patch(src_patch[hunk], files)
```

#### `toolkit_execute(target, project, wd, **kwargs)`
```python
def toolkit_execute(self, target: Any, project: str, wd: str, **kwargs) -> str:
    """
    Execute Java toolkit operations.
    
    Args:
        target: Target to execute (property name, Ant target, or test list)
        project: Project name
        wd: Working directory
        **kwargs: Additional arguments for toolkit_execute()
        
    Returns:
        str: Toolkit output
    """
    return toolkit_execute(target, project, wd, context=self.context, **kwargs)
```

## Built-in Loaders

### Chart (JFreeChart)

**Module**: `catena4j/loaders/Chart.py`

```python
class ChartLoader(ProjectLoader):
    version_control_system_class = Svn
    project_name = 'jfreechart'
    
    def determine_layout(self):
        return {
            'src': 'source',
            'test': 'tests'
        }
    
    def d4j_checkout_hook(self, project, revision_id, wd):
        return fix_compilation_errors(self.context, project, revision_id, wd)
```

**Characteristics**:
- VCS: Subversion (SVN)
- Repository: jfreechart
- Source directory: `source`
- Test directory: `tests`
- Post-checkout: Fixes compilation errors for certain revisions

### Math (Apache Commons Math)

**Module**: `catena4j/loaders/Math.py`

```python
class MathLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-math'
    
    def determine_layout(self):
        return {
            'src': [
                'src/main/java',
                'src/java'
            ],
            'test': [
                'src/test/java',
                'src/test'
            ]
        }
```

**Characteristics**:
- VCS: Git
- Repository: commons-math
- Multiple source layouts (handles both Maven and old structure)
- Multiple test layouts
- No special post-checkout hooks

### Lang (Apache Commons Lang)

**Module**: `catena4j/loaders/Lang.py`

```python
class LangLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'commons-lang'
    
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }
```

**Characteristics**:
- VCS: Git
- Repository: commons-lang
- Standard Maven layout
- Single source/test directory

### Closure (Closure Compiler)

**Module**: `catena4j/loaders/Closure.py`

```python
class ClosureLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'closure-compiler'
    
    def determine_layout(self):
        return {
            'src': ['src', 'gen'],
            'test': 'test'
        }
    
    def d4j_checkout_hook(self, project, revision_id, wd):
        # Custom build file handling
        return fix_missing_build_file(self.context, project, revision_id, wd)[2]
```

**Characteristics**:
- VCS: Git
- Repository: closure-compiler
- Multiple source directories (src + generated)
- Post-checkout: Handles missing build files

## Creating Custom Loaders

### Step-by-Step Guide

#### 1. Create Loader Class

Create `catena4j/loaders/MyProject.py`:

```python
from .project_loader import ProjectLoader
from ..util import Git  # or Svn

class MyProjectLoader(ProjectLoader):
    # Required: Specify VCS class
    version_control_system_class = Git
    
    # Required: Specify project name (repository name)
    project_name = 'myproject'
    
    # Required: Implement directory layout
    def determine_layout(self):
        """
        Return source and test directory layouts.
        
        Can return:
        - Single directory as string
        - Multiple directories as list
        """
        return {
            'src': 'src/main/java',  # Single directory
            'test': [                # Multiple directories
                'src/test/java',
                'src/integration-test/java'
            ]
        }
    
    # Optional: Post-checkout modifications
    def d4j_checkout_hook(self, project, revision_id, wd):
        """
        Perform project-specific modifications after checkout.
        
        Returns:
            bool: True if files were modified
        """
        # Example: Fix build configuration
        build_file = Path(wd) / 'build.xml'
        if not build_file.exists():
            # Copy default build file
            import shutil
            shutil.copy(
                self.context.c4j_home / 'resources' / 'default-build.xml',
                build_file
            )
            return True  # Files modified
        
        return False  # No modifications
    
    # Optional: Custom property retrieval
    def get_custom_property(self, property_name):
        """Custom property access logic"""
        # Use parent method for standard properties
        if property_name in ['tests.trigger', 'classes.modified']:
            return super().get_property(property_name, 
                                       self.project_name, 
                                       self.bid, 
                                       self.cid)
        
        # Custom logic for other properties
        return custom_computation(property_name)
```

#### 2. Register Loader

Edit `catena4j/bootstrap.py`:

```python
def initialize_loaders():
    from .loaders import register_loader_lazy
    
    def register_project_loader(proj: str):
        register_loader_lazy(proj, proj, f'{proj}Loader', 1)
    
    # Existing projects
    register_project_loader('Chart')
    register_project_loader('Math')
    # ... more projects ...
    
    # Add your project
    register_project_loader('MyProject')
```

#### 3. Add Project Metadata

Create directory structure:
```
projects/MyProject/
├── bugs-registry.csv
├── MyProject.export.xml
├── MyProject.compile.xml
└── patches/
    └── <bid>/
        └── <cid>/
            └── meta.json
```

**bugs-registry.csv**:
```csv
MyProject,1,1,MyProject
MyProject,1,2,MyProject
```

Format: `<project>,<bid>,<cid>,<loader_name>`

#### 4. Use Loader

```python
from catena4j.loaders import get_project_loader

# Get loader class
LoaderClass = get_project_loader('MyProject')

# Create instance
from catena4j.env import get_system_context
context = get_system_context()
loader = LoaderClass(context)

# Use loader
loader.checkout_revision('abc123', './work')
prop = loader.get_property('tests.trigger', 'MyProject', '1', '1')
```

## Advanced Loader Patterns

### Multiple Directory Layouts

Some projects have different layouts across versions:

```python
def determine_layout(self):
    """Handle version-specific layouts"""
    # Access context to determine version
    # Note: This is called early, so version info may not be available
    
    # Option 1: Return all possible layouts
    return {
        'src': [
            'src/main/java',   # Maven layout
            'src/java',        # Old layout
            'src'              # Oldest layout
        ],
        'test': [
            'src/test/java',
            'src/test'
        ]
    }
    
    # The build system will use the first existing directory
```

### Conditional Post-Checkout Operations

```python
def d4j_checkout_hook(self, project, revision_id, wd):
    """Apply fixes based on revision"""
    modified = False
    
    # Fix compilation errors for specific revision range
    if self._needs_compilation_fix(revision_id):
        fix_compilation_errors(self.context, project, revision_id, wd)
        modified = True
    
    # Fix missing dependencies for specific revisions
    if self._needs_dependency_fix(revision_id):
        self._fix_dependencies(wd)
        modified = True
    
    return modified

def _needs_compilation_fix(self, revision_id):
    """Check if revision needs compilation fixes"""
    # Implement logic to determine if fixes needed
    return int(revision_id) in range(10, 20)

def _needs_dependency_fix(self, revision_id):
    """Check if revision needs dependency fixes"""
    return int(revision_id) < 5

def _fix_dependencies(self, wd):
    """Fix missing dependencies"""
    # Copy dependency JARs, modify build files, etc.
    pass
```

### Custom VCS Operations

```python
class MyProjectLoader(ProjectLoader):
    version_control_system_class = Git
    project_name = 'myproject'
    
    def checkout_revision(self, revision_id, wd):
        """Custom checkout with submodules"""
        # Standard checkout
        result = super().checkout_revision(revision_id, wd)
        
        # Initialize submodules
        import subprocess
        subprocess.run(['git', 'submodule', 'update', '--init'],
                      cwd=wd,
                      check=True)
        
        return result
```

### Delegating to Helper Functions

```python
# loaders/my_project_helpers.py
def fix_build_configuration(context, project, revision_id, wd):
    """Fix build.xml for specific revisions"""
    from ..util import read_file, write_file
    from pathlib import Path
    
    build_file = Path(wd) / 'build.xml'
    content = read_file(build_file)
    
    # Modify content
    modified_content = content.replace('old-value', 'new-value')
    
    if content != modified_content:
        write_file(build_file, modified_content)
        return True
    
    return False

# loaders/MyProject.py
from .my_project_helpers import fix_build_configuration

class MyProjectLoader(ProjectLoader):
    # ...
    
    def d4j_checkout_hook(self, project, revision_id, wd):
        return fix_build_configuration(self.context, project, revision_id, wd)
```

## Loader Utilities

### Post-Checkout Utilities (`post_checkout_util.py`)

Common helper functions for post-checkout operations.

#### `fix_compilation_errors(context, project, revision_id, wd)`
```python
def fix_compilation_errors(context, project, revision_id, wd) -> bool:
    """
    Apply compilation error fixes from Defects4J.
    
    Searches for patches in:
    d4j_home/framework/projects/<project>/compile-errors/
    
    Returns:
        bool: True if patches were applied
    """
```

Applies patches for known compilation issues in specific revision ranges.

#### `fix_missing_build_file(context, project, revision_id, wd)`
```python
def fix_missing_build_file(context, project, revision_id, wd) -> tuple:
    """
    Copy build files if missing in working directory.
    
    Returns:
        tuple: (project_dir, wd_path, modified, build_file_path)
    """
```

Handles cases where older revisions don't include build files.

### Usage Example

```python
from .post_checkout_util import fix_compilation_errors, fix_missing_build_file

class MyLoader(ProjectLoader):
    def d4j_checkout_hook(self, project, revision_id, wd):
        modified = False
        
        # Fix compilation errors
        if fix_compilation_errors(self.context, project, revision_id, wd):
            modified = True
        
        # Fix missing build files
        _, _, build_modified, _ = fix_missing_build_file(
            self.context, project, revision_id, wd
        )
        if build_modified:
            modified = True
        
        return modified
```

## Loader Registration

### Direct Registration

```python
from catena4j.loaders import register_loader

class MyLoader(ProjectLoader):
    # ...

register_loader('MyProject', MyLoader)
```

### Lazy Registration (Recommended)

```python
from catena4j.loaders import register_loader_lazy

# Register without importing
register_loader_lazy('MyProject', 'MyProject', 'MyProjectLoader', 1)

# Parameters:
# - 'MyProject': Loader name
# - 'MyProject': Module name (relative to loaders/)
# - 'MyProjectLoader': Class name
# - 1: Import level (1 for relative import)
```

**Benefits**:
- Faster startup (loaders loaded only when needed)
- Reduced memory usage
- Better modularity

### Project-Loader Mapping

Override which loader is used for a project:

```python
from catena4j.loaders import set_project_loader

# Use DefaultLoader for MyProject
set_project_loader('MyProject', 'default')

# Use CustomLoader for MyProject
set_project_loader('MyProject', 'CustomLoader')
```

**Loader Resolution Order**:
1. Explicit mapping via `set_project_loader()`
2. Loader with same name as project
3. 'default' loader (if registered)

## Testing Loaders

### Unit Tests

```python
import unittest
from pathlib import Path
from catena4j.loaders.MyProject import MyProjectLoader
from catena4j.env import get_system_context

class TestMyProjectLoader(unittest.TestCase):
    def setUp(self):
        self.context = get_system_context()
        self.loader = MyProjectLoader(self.context)
    
    def test_layout_determination(self):
        layout = self.loader.determine_layout()
        self.assertIn('src', layout)
        self.assertIn('test', layout)
    
    def test_vcs_type(self):
        from catena4j.util import Git
        self.assertIsInstance(self.loader.version_control_system, Git)
    
    def test_property_access(self):
        prop = self.loader.get_property('tests.trigger', 
                                        'MyProject', '1', '1')
        self.assertIsInstance(prop, str)
```

### Integration Tests

```bash
#!/bin/bash
# Test loader end-to-end

PROJECT="MyProject"
BID="1"
CID="1"
WORKDIR="./test_workspace"

# Checkout using loader
catena4j checkout -p $PROJECT -v ${BID}b${CID} -w $WORKDIR

# Verify checkout
if [ -d "$WORKDIR/src" ]; then
    echo "PASS: Source directory created"
else
    echo "FAIL: Source directory missing"
    exit 1
fi

# Cleanup
rm -rf $WORKDIR
```

## Best Practices

### DO

✅ **Use Lazy Registration** for better performance
✅ **Return multiple directory possibilities** in `determine_layout()`
✅ **Document post-checkout modifications** in comments
✅ **Use helper functions** for reusable logic
✅ **Return True from `d4j_checkout_hook`** only when files modified
✅ **Handle both old and new layouts** in multi-version projects
✅ **Cache expensive computations** in loader instance

### DON'T

❌ **Don't modify context** in loader methods
❌ **Don't perform expensive operations** in `__init__`
❌ **Don't hard-code paths** - use context attributes
❌ **Don't forget to call super().__init__()** in custom `__init__`
❌ **Don't apply global modifications** - keep changes scoped to working directory
❌ **Don't assume version information available** in `determine_layout()`

## Troubleshooting

### Issue: Loader Not Found

**Symptom**: `LoaderError: No loader found for project MyProject`

**Solutions**:
1. Ensure loader is registered in `bootstrap.initialize_loaders()`
2. Check loader class name matches registration
3. Verify module name is correct for lazy registration

### Issue: Wrong Directories Used

**Symptom**: Build fails because source files not found

**Solutions**:
1. Check `determine_layout()` returns correct paths
2. Verify paths exist in checked-out working directory
3. Return list of possible paths if layout varies

### Issue: Post-Checkout Hook Not Running

**Symptom**: Expected modifications not applied

**Solutions**:
1. Ensure `d4j_checkout_hook()` is implemented
2. Check return value (True if modified, False otherwise)
3. Verify hook is called in checkout command flow

## See Also

- [API Reference](API.md) - Loader API details
- [Commands Guide](commands.md) - How commands use loaders
- [Utilities Guide](utilities.md) - Helper functions
- [Architecture](ARCHITECTURE.md) - Loader system design
