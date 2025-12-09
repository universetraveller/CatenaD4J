# CatenaD4J User Guide

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
  - [Docker Installation](#docker-installation)
  - [Manual Installation](#manual-installation)
- [Quick Start](#quick-start)
- [Available Commands](#available-commands)
- [Command Reference](#command-reference)
  - [checkout](#checkout)
  - [export](#export)
  - [test](#test)
  - [compile](#compile)
  - [clean](#clean)
  - [reset](#reset)
  - [pids](#pids)
  - [bids](#bids)
  - [cids](#cids)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Introduction

CatenaD4J (c4j) is a dataset for evaluating automated program repair techniques on indivisible multi-hunk bugs. A "catena bug" consists of multiple interdependent code hunks that must all be fixed together to resolve the bug.

### Key Features
- **367 bugs** across 6 projects from Defects4J
- **Minimal, isolated bugs** with single-assertion failing tests
- **Indivisible multi-hunk** structure requiring coordinated fixes
- **Compatible with Defects4J** as a plugin/extension
- **Extensible architecture** supporting custom commands and loaders

### Bug Structure
Each bug in CatenaD4J has:
- A unique `catena_id (cid)` identifier
- Association with a source Defects4J `bug_id (bid)`
- Minimal failing tests with single assertions
- Multiple interdependent code hunks

Bugs are referenced using the format: `<bug_id><b/f><cid>`
- `bug_id`: Original Defects4J bug number
- `b/f`: Buggy or fixed version
- `cid`: CatenaD4J catena identifier

## Installation

### Requirements
- **Python 3**: Pre-installed on most Linux/macOS systems
- **Defects4J v2.0**: See [defects4j repository](https://github.com/rjust/defects4j.git)
- **Java 1.8 (JDK 8)**: See [OpenJDK 8](https://openjdk.org/projects/jdk8/)

### Docker Installation

The easiest way to get started is using Docker.

1. **Install Docker** (if not already installed):
   - Follow instructions at [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **Download the Dockerfile**:
   ```bash
   curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/Dockerfile -o Dockerfile
   ```

3. **Build the Docker image**:
   ```bash
   docker build -t catena4j:main -f ./Dockerfile .
   ```

4. **Create and run a container**:
   ```bash
   docker run -it catena4j:main /bin/bash
   ```

### Manual Installation

For native installation without Docker:

1. **Install Prerequisites**:
   - Install Python 3, Java 8, and Defects4J v2.0 (see Requirements above)

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/universetraveller/CatenaD4J.git
   cd CatenaD4J
   ```

3. **Build the Java Toolkit**:
   ```bash
   cd toolkit
   bash compile.sh
   cd ..
   ```

4. **Install Using setup.py** (recommended):
   ```bash
   python3 setup.py install
   ```
   
   Or use the provided startup script:
   
5. **Add to PATH** (if using the startup script):
   ```bash
   export PATH=$PATH:/path/to/CatenaD4J
   ```

6. **Verify Installation**:
   ```bash
   catena4j pids
   ```

### Using setup_unix_user.py

For custom installation with a user-specified startup script:

```bash
python3 setup_unix_user.py -n <script_name> -p <python_path>
```

Options:
- `-n, --name`: Name of the startup script to generate (default: `c4j`)
- `-p, --python`: Path to Python interpreter (default: current Python executable)

This will:
1. Build the Java toolkit
2. Generate a startup script with your chosen name
3. Add the script to your PATH (in `.bashrc`, `.zshrc`, or `.profile`)

## Quick Start

1. **List available projects**:
   ```bash
   catena4j pids
   ```

2. **List bugs for a project**:
   ```bash
   catena4j bids -p Chart
   ```

3. **List catena IDs for a specific bug**:
   ```bash
   catena4j cids -p Chart -b 15
   ```

4. **Check out a buggy version**:
   ```bash
   catena4j checkout -p Chart -v 15b1 -w ./buggy_chart
   ```

5. **Compile the checked-out version**:
   ```bash
   catena4j compile -w ./buggy_chart
   ```

6. **Run tests**:
   ```bash
   catena4j test -w ./buggy_chart --trigger
   ```

7. **Export properties**:
   ```bash
   catena4j export -p tests.trigger -w ./buggy_chart
   ```

## Available Commands

| Command   | Description                                              |
|-----------|----------------------------------------------------------|
| checkout  | Check out a specific version of a bug                    |
| export    | Export version-specific properties                       |
| test      | Run tests on a checked-out project version               |
| compile   | Compile a checked-out project version                    |
| clean     | Clean the output directory                               |
| reset     | Reset unstaged modifications in a working directory      |
| pids      | Print available project names                            |
| bids      | Print available bug IDs for a project                    |
| cids      | Print available catena IDs for a bug                     |

## Command Reference

### checkout

Check out a specific version of a bug to a working directory.

**Syntax**:
```bash
catena4j checkout -p <project> -v <version_id> -w <work_dir> [--full-history]
```

**Options**:
- `-p <project>`: Project name (required)
- `-v <version_id>`: Version identifier in format `<bid><b/f><cid>` (required)
  - `bid`: Bug ID (integer)
  - `b/f`: 'b' for buggy, 'f' for fixed
  - `cid`: Catena ID (integer)
- `-w <work_dir>`: Working directory path (required)
- `--full-history`: Generate additional commits (post-fix, pre-fix revisions)

**Examples**:
```bash
# Check out buggy version of Chart bug 15, catena ID 1
catena4j checkout -p Chart -v 15b1 -w ./chart_15b1

# Check out fixed version
catena4j checkout -p Chart -v 15f1 -w ./chart_15f1

# Check out with full history
catena4j checkout -p Chart -v 15b1 -w ./chart_15b1 --full-history
```

### export

Export version-specific properties of a checked-out bug.

**Syntax**:
```bash
catena4j export -p <property> [-w <work_dir>] [-o <output_file>] [--from-cache] [--update-cache]
```

**Options**:
- `-p <property>`: Property name to export (required)
- `-w <work_dir>`: Working directory (default: current directory)
- `-o <output_file>`: Output file path (default: stdout)
- `--from-cache`: Read from cache instead of computing
- `--update-cache`: Force cache update

**Available Properties**:

*CatenaD4J Properties*:
- `classes.modified`: Classes modified by the bug fix
- `tests.trigger`: Trigger tests that expose the bug

*Defects4J Static Properties*:
- `classes.relevant`: Classes loaded by triggering tests
- `dir.src.classes`: Source directory of classes
- `dir.src.tests`: Source directory of tests
- `tests.relevant`: Tests touching modified sources

*Defects4J Dynamic Properties* (computed at runtime):
- `cp.compile`: Classpath to compile the project
- `cp.test`: Classpath for tests
- `dir.bin.classes`: Target directory of classes
- `dir.bin.tests`: Target directory of test classes
- `tests.all`: List of all developer-written tests

**Examples**:
```bash
# Export trigger tests to stdout
catena4j export -p tests.trigger -w ./chart_15b1

# Export to file
catena4j export -p classes.modified -w ./chart_15b1 -o modified.txt

# Use cache
catena4j export -p tests.all -w ./chart_15b1 --from-cache
```

### test

Run tests on a checked-out project version.

**Syntax**:
```bash
catena4j test [-w <work_dir>] [-c] [-l] [-i <level>] [-t <test> | -r | --trigger]
```

**Options**:
- `-w <work_dir>`: Working directory (default: current directory)
- `-c, --compile`: Compile before running tests
- `-l, --list`: List tests without executing them (output to `<work_dir>/all_tests`)
- `-i, --isolation <level>`: Test isolation level (default: from config)
  - `1`: Reused isolated classloader (fastest)
  - `2`: Isolated classloader per test class
  - `3`: Use Ant's JUnit task (slowest, most isolated)
- `-t <test>`: Run specific test(s) in format `ClassName#methodName` (can be repeated)
- `-r`: Run only relevant tests
- `--trigger`: Run only trigger tests
- `-a`: Collect failed assertions without breaking (experimental)

**Examples**:
```bash
# Run all tests
catena4j test -w ./chart_15b1

# Compile and run trigger tests
catena4j test -w ./chart_15b1 -c --trigger

# Run specific test
catena4j test -w ./chart_15b1 -t org.jfree.chart.ChartTest#testMethod

# List all tests without running
catena4j test -w ./chart_15b1 -l

# Run with maximum isolation
catena4j test -w ./chart_15b1 -i 3
```

### compile

Compile a checked-out project version.

**Syntax**:
```bash
catena4j compile [-w <work_dir>] [--target <target>] [--verbose]
```

**Options**:
- `-w <work_dir>`: Working directory (default: current directory)
- `--target <target>`: Compilation target (default: `compile.tests`)
  - Must contain 'compile' or be 'clean'
  - Examples: `compile`, `compile.tests`, `gradle.compile`
- `--verbose`: Show detailed compilation output

**Examples**:
```bash
# Compile tests (default)
catena4j compile -w ./chart_15b1

# Compile only classes
catena4j compile -w ./chart_15b1 --target compile

# Verbose compilation
catena4j compile -w ./chart_15b1 --verbose
```

### clean

Clean the build output directory.

**Syntax**:
```bash
catena4j clean [-w <work_dir>] [--verbose]
```

**Options**:
- `-w <work_dir>`: Working directory (default: current directory)
- `--verbose`: Show detailed output

**Example**:
```bash
catena4j clean -w ./chart_15b1
```

### reset

Reset all unstaged modifications in a working directory.

**Syntax**:
```bash
catena4j reset [-w <work_dir>]
```

**Options**:
- `-w <work_dir>`: Working directory to reset (default: current directory)

**Example**:
```bash
catena4j reset -w ./chart_15b1
```

### pids

Print all available project names in the dataset.

**Syntax**:
```bash
catena4j pids
```

**Example Output**:
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

Print available bug IDs for a specific project.

**Syntax**:
```bash
catena4j bids -p <project> [--with-cids] [-D | -A]
```

**Options**:
- `-p <project>`: Project name (required)
- `--with-cids`: Show only bug IDs that have at least one catena ID
- `-D`: Show deprecated bug IDs
- `-A`: Show all bug IDs (active and deprecated)

**Examples**:
```bash
# Show active bugs
catena4j bids -p Chart

# Show bugs with catena IDs
catena4j bids -p Chart --with-cids

# Show all bugs including deprecated
catena4j bids -p Chart -A
```

### cids

Print available catena IDs for a specific bug.

**Syntax**:
```bash
catena4j cids -p <project> -b <bug_id>
```

**Options**:
- `-p <project>`: Project name (required)
- `-b <bug_id>`: Bug ID (required)

**Example**:
```bash
catena4j cids -p Chart -b 15
```

## Configuration

CatenaD4J configuration is defined in `catena4j/config.py`. Key settings include:

### Global Settings
- `cli_program`: CLI program name (default: `'catena4j'`)
- `rich_output`: Enable colored and enhanced output (default: `True`)
- `minimal_checkout`: Skip unnecessary commit processes (default: `True`)

### Paths
- `c4j_rel_projects`: Relative path to projects directory
- `c4j_rel_toolkit_lib`: Path to compiled Java toolkit JAR
- `d4j_rel_ant_path`: Path to Defects4J Ant binaries
- `d4j_rel_projects`: Path to Defects4J projects metadata

### Testing
- `c4j_test_isolation_level`: Default test isolation level (default: `1`)
  - `1`: Reused isolated classloader
  - `2`: Isolated classloader per test class
  - `3`: Ant's JUnit task

### Toolkit Java Classes
- `c4j_toolkit_export_main`: Main class for export operations
- `c4j_toolkit_test_main`: Main class for test execution
- `c4j_toolkit_execute_main`: Main class for general execution

### Version Tags
- `c4j_tag`: Tag format for CatenaD4J versions
- `d4j_tag`: Tag format for Defects4J versions

To customize configuration, modify `catena4j/config.py` before installation or use the extensibility APIs to override settings programmatically.

## Examples

### Working with a Single Bug

```bash
# Create a workspace
mkdir -p workspace && cd workspace

# Check out a buggy version
catena4j checkout -p Math -v 5b1 -w ./math_5b1

# Navigate to working directory
cd math_5b1

# Export trigger tests
catena4j export -p tests.trigger -w .

# Compile the project
catena4j compile -w .

# Run trigger tests
catena4j test -w . --trigger

# Export modified classes
catena4j export -p classes.modified -w . -o modified_classes.txt

# Reset modifications
catena4j reset -w .
```

### Batch Processing Multiple Bugs

```bash
#!/bin/bash

PROJECT="Chart"
BUGS=$(catena4j bids -p $PROJECT --with-cids)

for BID in $BUGS; do
  CIDS=$(catena4j cids -p $PROJECT -b $BID)
  for CID in $CIDS; do
    VERSION="${BID}b${CID}"
    WORKDIR="./workspace/${PROJECT}_${VERSION}"
    
    echo "Processing $PROJECT bug $VERSION"
    catena4j checkout -p $PROJECT -v $VERSION -w $WORKDIR
    catena4j compile -w $WORKDIR
    catena4j test -w $WORKDIR --trigger > "${WORKDIR}/test_results.txt"
  done
done
```

### Using Cache for Performance

```bash
# First run: compute and cache
catena4j export -p tests.all -w ./chart_15b1 --update-cache

# Subsequent runs: use cached results (much faster)
catena4j export -p tests.all -w ./chart_15b1 --from-cache

# Force cache refresh
catena4j export -p tests.all -w ./chart_15b1 --update-cache
```

## Troubleshooting

### Common Issues

**Issue**: `catena4j: command not found`
- **Solution**: Ensure CatenaD4J is in your PATH or use the full path to the script
  ```bash
  export PATH=$PATH:/path/to/CatenaD4J
  ```

**Issue**: Python encoding errors
- **Solution**: Set the encoding environment variable:
  ```bash
  export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
  ```

**Issue**: Defects4J not found
- **Solution**: Install Defects4J v2.0 and ensure it's in your PATH
  ```bash
  which defects4j  # Should show the path
  ```

**Issue**: Java compilation errors
- **Solution**: Ensure Java 1.8 (JDK 8) is installed and active
  ```bash
  java -version  # Should show 1.8.x
  ```

**Issue**: Checkout fails for a specific bug
- **Solution**: Check if the bug ID and catena ID combination is valid
  ```bash
  catena4j cids -p <project> -b <bug_id>
  ```

**Issue**: Tests fail unexpectedly
- **Solution**: Try different isolation levels
  ```bash
  catena4j test -w ./workdir -i 3  # Use highest isolation
  ```

### Known Issues

**Flaky Bugs in Mockito**: Some bugs in the Mockito project produce varying test results in different environments (sequential vs. parallel execution, high CPU usage). It's recommended to avoid Mockito project bugs until this is resolved.

### Getting Help

- **Issues**: Report bugs at [GitHub Issues](https://github.com/universetraveller/CatenaD4J/issues)
- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- **API Reference**: See [API.md](API.md) for programmatic usage
- **Defects4J Documentation**: [Defects4J Repository](https://github.com/rjust/defects4j)

### Environment Variables

CatenaD4J respects the following environment variables:
- `TZ`: Timezone (default: `America/Los_Angeles`)
- `PATH`: Must include Defects4J and CatenaD4J
- `JAVA_TOOL_OPTIONS`: Java options (recommended: `-Dfile.encoding=UTF8`)
- `GRADLE_LOCAL_HOME_DIR`: Gradle home for projects using Gradle

## Next Steps

- **Understand the Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Programming**: See [API.md](API.md) for using CatenaD4J as a library
- **Extend CatenaD4J**: Learn about loaders and commands in the component guides
- **Reproduce Experiments**: Follow instructions in `scripts/README.md`

## References

- **Paper**: Q. Xin, H. Wu, J. Tang, X. Liu, S. Reiss and J. Xuan. "Detecting, Creating, Evaluating, and Understanding Indivisible Multi-Hunk Bugs." FSE 2024.
- **Repository**: [https://github.com/universetraveller/CatenaD4J](https://github.com/universetraveller/CatenaD4J)
- **Defects4J**: [https://github.com/rjust/defects4j](https://github.com/rjust/defects4j)
