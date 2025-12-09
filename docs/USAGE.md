# CatenaD4J Usage Guide

This guide provides comprehensive instructions for using CatenaD4J, a dataset for evaluating techniques on repairing indivisible multi-hunk bugs.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Command Reference](#command-reference)
- [Common Workflows](#common-workflows)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Overview

CatenaD4J (c4j) is a dataset that works as a plugin to other datasets (primarily Defects4J). It provides tools for detecting and creating indivisible bugs - bugs where multiple code hunks depend on each other and must all be fixed together.

### Key Concepts

- **Catena Bug**: An isolated, minimal bug consisting of multiple hunks that depend on each other
- **Catena ID (cid)**: Unique identifier for bugs generated from the same source bug
- **Bug Version**: Tagged as `<bug_id><b/f><cid>` where b/f indicates buggy/fixed version
- **Loader**: Component responsible for loading bug information and executing commands

## Getting Started

### Prerequisites

Before using CatenaD4J, ensure you have:

- Python 3.x
- Defects4J v2.0
- Java 1.8 (JDK 8)

### Installation

Refer to the [main README](../README.md#installation) for installation instructions using either Docker or manual setup.

### Verifying Installation

After installation, verify everything is working:

```bash
# Check that catena4j is in your PATH
catena4j pids

# This should list all available project names
```

## Command Reference

### checkout

Check out a specific version of a bug to a working directory.

**Syntax:**
```bash
catena4j checkout -p <project_name> -v <version_id> -w <work_dir> [--full-history]
```

**Arguments:**
- `-p <project_name>`: Project identifier (e.g., Chart, Lang, Math)
- `-v <version_id>`: Version in format `<bug_id><b/f><cid>`
  - `<bug_id>`: Integer bug ID from Defects4J
  - `<b/f>`: Either 'b' (buggy) or 'f' (fixed)
  - `<cid>`: Catena ID (integer)
- `-w <work_dir>`: Target working directory (will be created if doesn't exist)
- `--full-history`: (Optional) Generate additional commits for post-fix revisions

**Examples:**
```bash
# Check out buggy version of Chart bug 15, catena id 1
catena4j checkout -p Chart -v 15b1 -w ./buggy

# Check out fixed version of Math bug 2, catena id 3
catena4j checkout -p Math -v 2f3 -w ./fixed

# Check out with full history
catena4j checkout -p Lang -v 10b1 -w ./lang_10 --full-history
```

**What it does:**
- Clones the bug repository to the working directory
- Applies the appropriate patches
- Initializes git repository with relevant tags
- Creates version metadata files

### export

Export version-specific properties from a checked-out bug.

**Syntax:**
```bash
catena4j export -p <property_name> [-w <work_dir>] [-o <output_file>] [--from-cache] [--update-cache]
```

**Arguments:**
- `-p <property_name>`: Property to export (see available properties below)
- `-w <work_dir>`: (Optional) Working directory path (defaults to current directory)
- `-o <output_file>`: (Optional) Output file path (defaults to stdout)
- `--from-cache`: Try to read result from cache instead of computing
- `--update-cache`: Force cache update even if cache exists

**Available Properties:**

*CatenaD4J Properties:*
- `classes.modified`: Classes modified by the bug fix
- `tests.trigger`: Trigger tests that expose the bug

*Static Defects4J Properties:*
- `classes.relevant`: Classes loaded by the triggering tests
- `dir.src.classes`: Source directory of classes
- `dir.src.tests`: Source directory of tests
- `tests.relevant`: Relevant tests touching modified sources

*Dynamic Defects4J Properties:*
- `cp.compile`: Classpath to compile the project
- `cp.test`: Classpath to compile and run tests
- `dir.bin.classes`: Target directory of classes
- `dir.bin.tests`: Target directory of test classes
- `tests.all`: List of all developer-written tests

**Examples:**
```bash
# Export modified classes to stdout
catena4j export -p classes.modified -w ./buggy

# Export trigger tests to a file
catena4j export -p tests.trigger -w ./buggy -o triggers.txt

# Export compile classpath using cache
catena4j export -p cp.compile -w ./buggy --from-cache

# Update cached property value
catena4j export -p tests.all -w ./buggy --update-cache
```

**Performance Tips:**
- Use `--from-cache` for frequently accessed properties
- Dynamic properties (cp.*, tests.all) are computed via build files and may be slower
- Cache is stored per-project/bug/property combination

### reset

Reset all unstaged modifications in a working directory.

**Syntax:**
```bash
catena4j reset [-w <work_dir>]
```

**Arguments:**
- `-w <work_dir>`: (Optional) Working directory to reset (defaults to current directory)

**Examples:**
```bash
# Reset current directory
catena4j reset

# Reset specific working directory
catena4j reset -w ./buggy
```

**Warning:** This command discards all unstaged changes. Use with caution.

### pids

Print all available project names/identifiers.

**Syntax:**
```bash
catena4j pids
```

**Example Output:**
```
Chart
Cli
Closure
Codec
Collections
Compress
...
```

### bids

Print all available bug IDs for a specific project that contain at least one catena ID.

**Syntax:**
```bash
catena4j bids -p <project_name>
```

**Arguments:**
- `-p <project_name>`: Project identifier

**Examples:**
```bash
# List all bug IDs for Chart project
catena4j bids -p Chart

# List all bug IDs for Math project
catena4j bids -p Math
```

### cids

Print all available catena IDs for a specific bug.

**Syntax:**
```bash
catena4j cids -p <project_name> -b <bug_id>
```

**Arguments:**
- `-p <project_name>`: Project identifier
- `-b <bug_id>`: Bug ID from Defects4J

**Examples:**
```bash
# List all catena IDs for Chart bug 15
catena4j cids -p Chart -b 15

# List all catena IDs for Math bug 2
catena4j cids -p Math -b 2
```

### Not Yet Implemented Commands

The following commands are planned but not yet implemented. They will be passed to the Defects4J backend:

- `info`: Display bug information
- `test`: Run tests for a checked-out bug
- `compile`: Compile a checked-out bug
- `ver`: Display version information

**Note:** You can still use these commands and they will be forwarded to Defects4J if available.

## Common Workflows

### Workflow 1: Exploring Available Bugs

```bash
# 1. List all projects
catena4j pids

# 2. List bugs in a specific project
catena4j bids -p Chart

# 3. List catena IDs for a specific bug
catena4j cids -p Chart -b 15
```

### Workflow 2: Checking Out and Analyzing a Bug

```bash
# 1. Create working directory and checkout buggy version
mkdir -p /tmp/analysis
catena4j checkout -p Chart -v 15b1 -w /tmp/analysis/chart15b1

# 2. Export trigger tests
catena4j export -p tests.trigger -w /tmp/analysis/chart15b1 -o triggers.txt

# 3. Export modified classes
catena4j export -p classes.modified -w /tmp/analysis/chart15b1 -o modified.txt

# 4. Get compile classpath
catena4j export -p cp.compile -w /tmp/analysis/chart15b1 -o classpath.txt

# 5. View the exported information
cat triggers.txt
cat modified.txt
```

### Workflow 3: Comparing Buggy and Fixed Versions

```bash
# 1. Checkout buggy version
catena4j checkout -p Math -v 2b1 -w /tmp/math2_buggy

# 2. Checkout fixed version
catena4j checkout -p Math -v 2f1 -w /tmp/math2_fixed

# 3. Export properties from both
catena4j export -p classes.modified -w /tmp/math2_buggy -o buggy_classes.txt
catena4j export -p classes.modified -w /tmp/math2_fixed -o fixed_classes.txt

# 4. Compare the differences
diff -u buggy_classes.txt fixed_classes.txt
```

### Workflow 4: Batch Processing Multiple Bugs

```bash
#!/bin/bash
# Process all catena IDs for a specific bug

PROJECT="Chart"
BUG_ID="15"

# Get all catena IDs
CIDS=$(catena4j cids -p $PROJECT -b $BUG_ID)

# Process each catena ID
for CID in $CIDS; do
    echo "Processing $PROJECT-$BUG_ID-$CID"
    
    WORK_DIR="/tmp/${PROJECT}_${BUG_ID}_${CID}"
    
    # Checkout buggy version
    catena4j checkout -p $PROJECT -v "${BUG_ID}b${CID}" -w "$WORK_DIR"
    
    # Export and analyze
    catena4j export -p tests.trigger -w "$WORK_DIR" -o "${WORK_DIR}_triggers.txt"
    catena4j export -p classes.modified -w "$WORK_DIR" -o "${WORK_DIR}_classes.txt"
    
    echo "Completed $PROJECT-$BUG_ID-$CID"
done
```

### Workflow 5: Using Cache for Performance

```bash
# First run computes and caches
catena4j export -p cp.compile -w ./buggy --update-cache

# Subsequent runs use cached value (much faster)
catena4j export -p cp.compile -w ./buggy --from-cache

# Force recalculation and cache update
catena4j export -p cp.compile -w ./buggy --update-cache
```

## Advanced Usage

### Understanding Bug Registry

Each project has a `bugs-registry.csv` file that defines all active bugs:

```
<project_name>, <bug_id>, <cid>, <loader>
```

Location: `./projects/<project_name>/bugs-registry.csv`

Example:
```
Chart,15,1,default
Chart,15,2,default
Math,2,1,default
```

### Custom Loaders

Projects can have custom loaders to handle project-specific build configurations. Current loaders:

- `default`: Standard loader for most projects
- Project-specific loaders: Chart, Cli, Closure, Codec, Collections, etc.

### Working with Git Repositories

Checked-out bugs are git repositories with tags:

```bash
cd /tmp/buggy

# List all tags
git tag

# Common tags:
# - <bug_id>b<cid>: Buggy version
# - <bug_id>f<cid>: Fixed version
# - <bug_id>b: Original buggy (if --full-history used)
# - <bug_id>f: Original fixed (if --full-history used)

# View differences between versions
git diff <bug_id>b<cid> <bug_id>f<cid>
```

### Environment Variables

CatenaD4J respects the following environment variables:

- `PATH`: Must include the directory containing the `catena4j` script
- `DEFECTS4J_HOME`: (Optional) Override default Defects4J location

### Configuration Files

CatenaD4J uses configuration files:

- `resources/defects4j.properties`: Defects4J integration settings
- Project-specific configs in `projects/<project>/` directories

## Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found: catena4j"

**Problem:** The `catena4j` script is not in your PATH.

**Solution:**
```bash
# Add to PATH (adjust path as needed)
export PATH=$PATH:/path/to/CatenaD4J

# Or use absolute path
/path/to/CatenaD4J/catena4j pids
```

#### 2. "Python not found"

**Problem:** Python 3 is not available or not in PATH.

**Solution:**
- Install Python 3 from https://www.python.org/
- Or edit the first line of `catena4j` script to point to your Python 3 executable

#### 3. Checkout fails with "Defects4J not found"

**Problem:** Defects4J backend is not properly installed.

**Solution:**
- Ensure Defects4J v2.0 is installed: https://github.com/rjust/defects4j
- Verify with: `defects4j info -p Chart`

#### 4. Export command is slow

**Problem:** Dynamic properties require build file processing.

**Solution:**
- Use `--from-cache` flag for repeated queries
- Consider using `--update-cache` once to populate cache

#### 5. "Working directory is not a valid CatenaD4J checkout"

**Problem:** Trying to export from a directory that wasn't checked out with `catena4j checkout`.

**Solution:**
- Ensure you use the correct working directory
- Re-checkout if metadata is corrupted

#### 6. Mockito project tests are flaky

**Known Issue:** Some Mockito bugs have flaky tests in different environments.

**Recommendation:** Avoid using Mockito project bugs for critical experiments.

### Getting Help

- Check the [main README](../README.md) for general information
- Review the [API documentation](API.md) for programmatic usage
- Visit the [GitHub repository](https://github.com/universetraveller/CatenaD4J)
- Open an issue for bugs or feature requests

### Debug Mode

For troubleshooting, you can enable verbose output:

```bash
# Use Python's verbose mode
python3 -v catena4j/bootstrap.py checkout -p Chart -v 15b1 -w ./test

# Or check the implementation directly
cd /path/to/CatenaD4J
python3 -c "from catena4j.bootstrap import system; system.start()"
```

## Performance Tips

1. **Use caching**: Enable `--from-cache` for repeated property exports
2. **Parallel processing**: Process multiple bugs in parallel using shell job control
3. **Selective exports**: Only export properties you need
4. **Reuse working directories**: Keep checkouts for reuse rather than re-checking out

## Best Practices

1. **Version control**: Keep your analysis scripts in version control
2. **Documentation**: Document which bugs and properties you use in experiments
3. **Reproducibility**: Record exact version IDs (`<bid><b/f><cid>`) used
4. **Clean up**: Use `reset` to clean working directories when needed
5. **Validation**: Always verify exports are correct for your use case

## Next Steps

- Explore the [Python API documentation](API.md) for programmatic usage
- Check the [Java Toolkit API](JAVA_API.md) for test execution tools
- Review [experimental scripts](../scripts/README.md) for advanced examples
- Read the FSE 2024 paper for theoretical background
