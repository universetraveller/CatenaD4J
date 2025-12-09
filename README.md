# CatenaD4J

CatenaD4J (c4j) is a dataset for evaluating techniques on repairing indivisible multi-hunk bugs. It contains tools for detecting and creating indivisible bugs where multiple code hunks depend on each other and must all be fixed together.

C4j works as a plugin to other datasets and uses Defects4J as the default backend. The dataset contains bugs generated from Defects4J, but it's designed to be easily extensible to other backends or custom commands.

> [!NOTE]
> Some bugs in the Mockito project have been found to be flaky, producing varying test results in different environments (e.g., sequential vs. parallel execution, or under high CPU usage). We recommend avoiding Mockito project bugs until this is resolved.

## Quick Links

- **[API Documentation](docs/)** - Python and Java API references
- **[Reproduce Experiments](scripts/README.md)** - Steps to reproduce FSE 2024 paper experiments

## Bugs in the Dataset

CatenaD4J contains **6 projects** and **367 bugs** generated from Defects4J.

- The dataset consists of original indivisible bugs from Defects4J and new isolated bugs created by dividing original bugs
- Each bug has failing tests containing only single assertion statements, preventing techniques from detecting partial fixes
- All bugs are **catena bugs** - catenated hunks that depend on each other and must all be fixed together
- Each bug has a `catena_id (cid)` for identification

**Bug Format:** `<bug_id><b/f><cid>` where b/f indicates buggy/fixed version

### Active Bugs

Check available bugs in `./projects/<project_name>/bugs-registry.csv`

Each line represents a catena bug: `<project_name>, <bug_id>, <cid>, <loader>`

## Requirements

* **Python 3** - Pre-installed on most Linux/MacOS systems ([download](https://www.python.org/downloads/))
* **Defects4J v2.0** - ([installation guide](https://github.com/rjust/defects4j.git))
* **Java 1.8** - JDK 8 ([download](https://openjdk.org/projects/jdk8/))

## Installation

### Using Docker

```bash
# Download Dockerfile
curl https://raw.githubusercontent.com/universetraveller/CatenaD4J/main/Dockerfile -o Dockerfile

# Build image
docker build -t catena4j:main -f ./Dockerfile .

# Run container
docker run -it catena4j:main /bin/bash
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/universetraveller/CatenaD4J.git

# Add to PATH
export PATH=$PATH:<path to CatenaD4J>

# Verify installation
catena4j pids
```

**Note:** The `catena4j` script requires `python3` command. Edit the first line of the script if your Python executable has a different name.

## Command-Line Usage

### Quick Start

```bash
# List available projects
catena4j pids

# List bugs in a project
catena4j bids -p Chart

# List catena IDs for a bug
catena4j cids -p Chart -b 15

# Check out a bug
catena4j checkout -p Chart -v 15b1 -w ./buggy

# Export bug properties
catena4j export -p tests.trigger -w ./buggy
```

### Command Reference

#### checkout - Check out a bug

```bash
catena4j checkout -p <project> -v <version_id> -w <work_dir> [--full-history]
```

**Arguments:**
- `-p`: Project name (Chart, Lang, Math, etc.)
- `-v`: Version ID in format `<bug_id><b/f><cid>` (e.g., 15b1)
  - `b` = buggy version, `f` = fixed version
- `-w`: Working directory (created if doesn't exist)
- `--full-history`: (Optional) Generate additional git commits

**Examples:**
```bash
# Check out buggy version
catena4j checkout -p Chart -v 15b1 -w ./chart_bug

# Check out fixed version
catena4j checkout -p Math -v 2f3 -w ./math_fixed

# With full history
catena4j checkout -p Lang -v 10b1 -w ./lang --full-history
```

#### export - Export bug properties

```bash
catena4j export -p <property> [-w <work_dir>] [-o <output_file>] [--from-cache] [--update-cache]
```

**Available Properties:**

*CatenaD4J Properties:*
- `classes.modified` - Classes modified by the bug fix
- `tests.trigger` - Trigger tests that expose the bug

*Defects4J Static Properties:*
- `classes.relevant` - Classes loaded by triggering tests
- `dir.src.classes` - Source directory of classes
- `dir.src.tests` - Source directory of tests  
- `tests.relevant` - Relevant tests touching modified sources

*Defects4J Dynamic Properties:*
- `cp.compile` - Classpath to compile the project
- `cp.test` - Classpath to run tests
- `dir.bin.classes` - Target directory of classes
- `dir.bin.tests` - Target directory of test classes
- `tests.all` - All developer-written tests

**Examples:**
```bash
# Export to stdout
catena4j export -p classes.modified -w ./buggy

# Export to file
catena4j export -p tests.trigger -w ./buggy -o triggers.txt

# Use cache (faster)
catena4j export -p cp.compile -w ./buggy --from-cache
```

#### Other Commands

```bash
# Reset working directory
catena4j reset [-w <work_dir>]

# List project IDs
catena4j pids

# List bug IDs for a project
catena4j bids -p <project>

# List catena IDs for a bug
catena4j cids -p <project> -b <bug_id>
```

**Not Yet Implemented:** `info`, `test`, `compile`, `ver` (forwarded to Defects4J backend)

### Common Workflows

#### Workflow 1: Explore Available Bugs

```bash
# List all projects
catena4j pids

# List bugs in Chart project
catena4j bids -p Chart

# List all variations of bug 15
catena4j cids -p Chart -b 15
```

#### Workflow 2: Analyze a Bug

```bash
# Check out the bug
catena4j checkout -p Chart -v 15b1 -w /tmp/chart15

# Get trigger tests
catena4j export -p tests.trigger -w /tmp/chart15 -o triggers.txt

# Get modified classes
catena4j export -p classes.modified -w /tmp/chart15 -o classes.txt

# View results
cat triggers.txt classes.txt
```

#### Workflow 3: Compare Buggy and Fixed

```bash
# Check out both versions
catena4j checkout -p Math -v 2b1 -w /tmp/math_buggy
catena4j checkout -p Math -v 2f1 -w /tmp/math_fixed

# Compare properties
catena4j export -p classes.modified -w /tmp/math_buggy -o buggy.txt
catena4j export -p classes.modified -w /tmp/math_fixed -o fixed.txt
diff -u buggy.txt fixed.txt
```

### Performance Tips

- Use `--from-cache` for frequently accessed properties (much faster)
- Dynamic properties (cp.*, tests.all) require build processing (slower)
- Export properties once and cache them with `--update-cache`

## API Documentation

For programmatic access to CatenaD4J, see the [API documentation](docs/):

- **[Python API](docs/)** - Commands, loaders, and utilities
- **[Java Toolkit API](docs/)** - Test runners, agents, and build integration

Example Python usage:
```python
from catena4j.dispatcher import ExecutionContext
from catena4j.commands import checkout, export
from argparse import Namespace

context = ExecutionContext()
context.args = Namespace(p='Chart', v='15b1', w='./bug', full_history=False)
checkout.run(context)

context.args = Namespace(p='tests.trigger', w='./bug', o=None, 
                        from_cache=False, update_cache=False)
result = export.run(context)
print(result)
```

## About Defects4J Backend

CatenaD4J uses Defects4J to checkout original bugs and supports `test` and `compile` commands through the backend. However, Defects4J is complex and relatively inefficient, calling Perl, Ant, and Java commands that execute slower than direct usage.

**Future Plans:** Re-implement Defects4J's checkout, test, and compile commands using Git and Java for better performance.

## Customization

CatenaD4J is designed with replaceable components for easy customization.

### Loaders

**Loaders** execute commands and load bug information. Each bug in `bugs-registry.csv` specifies its loader. Project-specific loaders are in `catena4j/loaders/`.

To create a custom loader:
1. Implement a loader class with `load`, `fix`, and `get_attr` methods
2. Add to `catena4j/loaders/`
3. Specify in `bugs-registry.csv`

### Commands

**Command entries** are the entry points for CLI commands. The CLI finds implementations from command entries and passes arguments.

To create a custom command:
1. Implement as a Python function processing args namespace
2. Add to command entries
3. Register in config

Example: `cids` command is implemented in `catena4j/commands/xids.py` and registered in the command system.

See [API documentation](docs/) for implementation details.

## Development Plan

The current version is stable and available. Future updates (developed as time permits):

1. Faster `test` command with abort-on-failure (JUnit 5 support)
2. Faster `checkout` command replacing Defects4J
3. Fast code coverage tool
4. Spectrum-based fault localization tool
5. Complete Defects4J backend replacement

## Repository Structure

```
CatenaD4J/
├── Dockerfile              # Docker build script
├── LICENSE                 # Apache 2.0 license
├── README.md               # This file
├── catena4j                # Main executable script
├── catena4j/               # Python implementation
│   ├── commands/           # Command implementations
│   ├── loaders/            # Project-specific loaders
│   └── ...                 # Core modules
├── docs/                   # API documentation
├── projects/               # Bug data and metadata
├── scripts/                # Experiment reproduction
│   ├── construct_database/ # Data preparation
│   ├── generate_bugs/      # Bug isolation algorithm
│   ├── parse_patches/      # Hunk extraction
│   └── split_tests/        # Test minimization
└── toolkit/                # Java utilities
    ├── src/                # Test runners and export
    └── junit-agent/        # JUnit instrumentation
```

## Statistics

See [statistics](scripts/generate_bugs/statstics) for current bug counts and details.

## Publications

* Q. Xin, H. Wu, J. Tang, X. Liu, S. Reiss and J. Xuan. "Detecting, Creating, Evaluating, and Understanding Indivisible Multi-Hunk Bugs." FSE 2024.

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.
