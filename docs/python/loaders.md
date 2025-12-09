# Python Loaders API

This document covers the loader system in CatenaD4J's Python API.

## Overview

Loaders are responsible for project-specific behavior during bug checkout and property export. Each project can have a custom loader to handle its unique requirements.

Package: `catena4j.loaders`

## Base Classes

### Class: `Loader`

Base class for all loaders.

**Package:** `catena4j.loaders.loader`

### Class: `ContextAwareLoader(Loader)`

Base class for loaders that need access to execution context.

**Constructor:**
```python
def __init__(self, context: ExecutionContext)
```

**Attributes:**
- `context`: ExecutionContext instance

## Project Loader

### Class: `ProjectLoader(ContextAwareLoader)`

Base class for project-specific loaders with common functionality.

**Package:** `catena4j.loaders.project_loader`

**Methods:**

```python
def get_property(self, prop: str, proj: str, bid: str, cid: str) -> str
```
Get a project-specific property value.

**Parameters:**
- `prop`: Property name
- `proj`: Project name
- `bid`: Bug ID
- `cid`: Catena ID

**Returns:** Property value as string

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

**Returns:** Property value as string

**Example:**
```python
from catena4j.dispatcher import ExecutionContext
from catena4j.loaders import get_project_loader

context = ExecutionContext()
LoaderClass = get_project_loader('Chart')
loader = LoaderClass(context)

# Get property
result = loader.get_property('tests.trigger', 'Chart', '15', '1')
print(result)
```

## Available Project Loaders

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

Each loader is in `catena4j/loaders/<ProjectName>.py` and may override default behavior for project-specific requirements.

## Getting a Project Loader

```python
from catena4j.loaders import get_project_loader

# Get loader class for a project
LoaderClass = get_project_loader('Chart')

# Instantiate with context
loader = LoaderClass(context)

# Use the loader
result = loader.get_property('tests.trigger', 'Chart', '15', '1')
```

## Creating a Custom Loader

To create a custom loader for a new project:

```python
from catena4j.loaders.project_loader import ProjectLoader

class MyProjectLoader(ProjectLoader):
    def get_property(self, prop, proj, bid, cid):
        # Custom property logic
        if prop == 'my.custom.property':
            return self._get_custom_property(proj, bid, cid)
        
        # Fall back to default implementation
        return super().get_property(prop, proj, bid, cid)
    
    def _get_custom_property(self, proj, bid, cid):
        # Your implementation
        return "custom value"
```

Then register it in `catena4j/loaders/__init__.py`.

## Loader Registry

Each bug in `projects/<project>/bugs-registry.csv` specifies its loader:

```
<project_name>, <bug_id>, <cid>, <loader>
```

Example:
```
Chart,15,1,default
Chart,15,2,Chart
Math,2,1,Math
```

The loader name maps to a class in the `catena4j.loaders` package.

## Post-Checkout Utilities

### Module: `catena4j.loaders.post_checkout_util`

Utilities for post-checkout operations.

**Functions:**

```python
def apply_post_checkout_fixes(proj: str, wd: Path, context: ExecutionContext)
```
Apply project-specific fixes after checkout.

**Parameters:**
- `proj`: Project name
- `wd`: Working directory path
- `context`: Execution context

## Example: Using Loaders

```python
from catena4j.dispatcher import ExecutionContext
from catena4j.loaders import get_project_loader
from pathlib import Path

# Initialize
context = ExecutionContext()

# Get Chart project loader
ChartLoader = get_project_loader('Chart')
loader = ChartLoader(context)

# Get trigger tests
tests = loader.get_property('tests.trigger', 'Chart', '15', '1')
print(f"Trigger tests:\n{tests}")

# Execute toolkit for dynamic property
classpath = loader.toolkit_execute(
    'cp.compile',
    'Chart',
    '/tmp/chart15',
    xml_attr='c4j_rel_project_export_xml',
    main_attr='c4j_toolkit_export_main'
)
print(f"Compile classpath: {classpath}")
```

## Best Practices

1. **Use existing loaders**: Don't create custom loaders unless necessary
2. **Override minimally**: Only override methods that need customization
3. **Test thoroughly**: Ensure custom loaders work with all bug IDs
4. **Document behavior**: Add comments explaining project-specific logic
5. **Handle errors**: Raise informative exceptions for edge cases

## See Also

- [Commands API](commands.md) - Command implementations that use loaders
- [Utilities API](utilities.md) - Helper functions used by loaders
- [Main README](../../README.md) - Dataset overview and structure
