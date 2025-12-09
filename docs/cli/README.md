# CLI Components Guide

## Overview

The CLI (Command-Line Interface) components provide the user-facing interface for CatenaD4J. This guide covers the internal implementation of CLI parsing, argument handling, and command dispatch.

## Module Structure

```
catena4j/cli/
├── __init__.py
├── manager.py      # CLI manager and command registration
└── parser.py       # Custom argument parsers
```

## Components

### Argument Parsers (`parser.py`)

Custom argument parser implementations that enhance the standard `argparse` functionality.

#### `RootArgumentParser`

Root-level argument parser with enhanced error handling.

**Features**:
- Custom error messages that include help text
- Better handling of unrecognized arguments
- Subparser navigation for targeted error messages

**Key Methods**:

##### `error(message: str)`
```python
def error(self, message: str):
    self._print_message(message + '\n', stderr)
    self.print_help(stderr)
    self.exit(2)
```

Override default error behavior to print help text along with error message.

**Example Output**:
```
unrecognized arguments: --invalid
usage: catena4j <command> [option]

Commands:
  checkout    Check out a particular project version
  export      Export a version-specific property
  ...
```

##### `parse_args(args=None, namespace=None)`
```python
def parse_args(self, args=None, namespace=None):
    args, argv = self.parse_known_args(args, namespace)
    if argv:
        parser = self._get_current_subparser(args)
        msg = _('unrecognized arguments: %s')
        parser.error(msg % ' '.join(argv))
    return args
```

Enhanced parsing that shows errors at the appropriate subcommand level.

**Usage**:
```python
from catena4j.cli.parser import RootArgumentParser

parser = RootArgumentParser(prog='catena4j')
# Add subparsers and arguments
args = parser.parse_args()
```

#### `RootHelpFormatter`

Custom help formatter for cleaner command listing.

**Features**:
- Simplified usage line for multiple subcommands
- Cleaner action formatting
- Removed redundant action headers

**Key Methods**:

##### `add_usage(usage, actions, groups, prefix=None)`
```python
def add_usage(self, usage, actions, groups, prefix=None):
    if actions:
        usage = _('%(prog)s <command> [option]')
    args = usage, actions, groups, prefix
    self._add_item(self._format_usage, args)
```

Simplifies usage line to `catena4j <command> [option]` when subcommands exist.

**Example**:
```
# Standard argparse:
usage: catena4j [-h] {checkout,export,test,compile,clean,...} ...

# RootHelpFormatter:
usage: catena4j <command> [option]
```

#### `LeafArgumentParser`

Parser for individual subcommands with controlled help output.

**Features**:
- Conditional argument help display via `__add_arguments_help__` attribute
- Consistent formatting across subcommands

**Key Methods**:

##### `format_help()`
```python
def format_help(self):
    formatter = self._get_formatter()
    formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)
    formatter.add_text(self.description)
    
    if getattr(self, '__add_arguments_help__', False):
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            for action in action_group._group_actions:
                if action.help:
                    formatter.add_argument(action)
            formatter.end_section()
    
    formatter.add_text(self.epilog)
    return formatter.format_help()
```

Only shows detailed argument help when `__add_arguments_help__ = True`.

**Usage**:
```python
from catena4j.cli.parser import LeafArgumentParser

parser = LeafArgumentParser(prog='catena4j export')
parser.add_argument('-p', required=True, help='Property name')
parser.__add_arguments_help__ = True  # Enable argument help
```

### CLI Manager (`manager.py`)

Manages command registration and parser initialization.

#### Module-Level Variables

```python
_root_parser = None  # Root argument parser
_subparsers = None   # Subparser action
```

Global references to parser infrastructure, initialized during bootstrap.

#### Functions

##### `init_root_parser(name, usage, description)`
```python
def init_root_parser(name='catena4j', usage=None, description=None):
    global _root_parser
    _root_parser = RootArgumentParser(
        prog=name,
        usage=usage,
        description=description,
        formatter_class=RootHelpFormatter,
        add_help=True
    )
```

Initialize the root CLI parser.

**Parameters**:
- `name`: Program name (default: from config)
- `usage`: Usage string (default: None for auto-generation)
- `description`: Program description (default: None)

**Called by**: `_bootstrap.initialize_cli()`

##### `_init_subcommands(title, dest, required)`
```python
def _init_subcommands(title='Commands', dest='command', required=True):
    global _subparsers
    _subparsers = _root_parser.add_subparsers(
        title=title,
        dest=dest,
        required=required
    )
```

Initialize subparser infrastructure for commands.

**Parameters**:
- `title`: Section title in help text
- `dest`: Attribute name for selected command
- `required`: Whether a command must be specified

**Called by**: `_bootstrap.initialize_cli()`

##### `_create_command(name, **kwargs)`
```python
def _create_command(name, **kwargs):
    return _subparsers.add_parser(name, parser_class=LeafArgumentParser, **kwargs)
```

Create a new command parser.

**Parameters**:
- `name`: Command name
- `**kwargs`: Arguments passed to `add_parser()`
  - `help`: Short description
  - `description`: Long description
  - `add_help`: Include -h/--help flag
  - `formatter_class`: Help formatter class

**Returns**: `LeafArgumentParser` for the command

**Usage**:
```python
from catena4j.cli.manager import _create_command

parser = _create_command('mycommand', 
                         help='My custom command',
                         add_help=False)
parser.add_argument('-p', required=True)
parser.__add_arguments_help__ = True
```

## CLI Initialization Flow

### Sequence

1. **Bootstrap Phase** (`_bootstrap.initialize_cli()`):
   ```python
   config = env._config
   init_root_parser(name=config.cli_program,
                    usage=config.cli_usage,
                    description=config.cli_description)
   _init_subcommands(title='Commands',
                     dest=config.cli_command_dest,
                     required=True)
   ```

2. **Command Registration** (`bootstrap.initialize_commands()`):
   ```python
   # For each command:
   from .commands import checkout
   checkout.initialize()  # Creates parser
   _register('checkout', checkout.run)  # Registers entry
   ```

3. **Argument Parsing** (`bootstrap.start_cli()`):
   ```python
   args = cli_manager._root_parser.parse_args()
   dest = env._config.cli_command_dest
   target = getattr(args, dest)
   delattr(args, dest)
   # Execute command...
   ```

### Example: Adding a Command

**Step 1: Create Command Module**

```python
# catena4j/commands/mycommand.py
from ..cli.manager import _create_command
from ..dispatcher import ExecutionContext

_parser = None

def initialize():
    global _parser
    _parser = _create_command('mycommand',
                              help='My custom command',
                              description='Detailed description',
                              add_help=False)
    _parser.add_argument('-p', required=True, metavar='parameter',
                         help='Parameter description')
    _parser.add_argument('--flag', action='store_true',
                         help='Flag description')
    _parser.__add_arguments_help__ = True

def run(context: ExecutionContext):
    args = context.args
    # Command implementation
    result = f"Executed with p={args.p}, flag={args.flag}"
    return result
```

**Step 2: Register in Bootstrap**

```python
# catena4j/bootstrap.py
def initialize_commands():
    from .commands import mycommand
    mycommand.initialize()
    _register('mycommand', mycommand.run)
```

**Step 3: Use Command**

```bash
catena4j mycommand -p value --flag
```

## Advanced Features

### Conditional Argument Help

Control whether detailed argument help is shown:

```python
parser = _create_command('command', add_help=False)
parser.add_argument('-a', help='Argument A')
parser.add_argument('-b', help='Argument B')

# Don't show argument details in help
# parser.__add_arguments_help__ = False  # Default

# Show argument details in help
parser.__add_arguments_help__ = True
```

**Without `__add_arguments_help__`**:
```
usage: catena4j command [options]

Description of command
```

**With `__add_arguments_help__`**:
```
usage: catena4j command [options]

Description of command

options:
  -a ARG        Argument A
  -b ARG        Argument B
```

### Custom Help Formatting

Use different formatters for different commands:

```python
from argparse import RawDescriptionHelpFormatter

parser = _create_command('command',
                         help='Short help',
                         description='Long\ndescription\nwith\nformatting',
                         formatter_class=RawDescriptionHelpFormatter)
```

**Available Formatters**:
- `HelpFormatter`: Default, wraps text
- `RawDescriptionHelpFormatter`: Preserves description formatting
- `RawTextHelpFormatter`: Preserves all formatting
- `ArgumentDefaultsHelpFormatter`: Shows default values

### Mutually Exclusive Groups

Create argument groups where only one can be used:

```python
parser = _create_command('command', add_help=False)
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('--option-a', action='store_true')
group.add_argument('--option-b', action='store_true')
```

**Usage**:
```bash
catena4j command --option-a  # OK
catena4j command --option-b  # OK
catena4j command --option-a --option-b  # ERROR
```

### Argument Actions

Built-in actions for common patterns:

**Boolean Flag**:
```python
parser.add_argument('--verbose', action='store_true')
```

**Append to List**:
```python
parser.add_argument('-t', action='append', metavar='test')
# catena4j command -t test1 -t test2
# args.t = ['test1', 'test2']
```

**Store Constant**:
```python
parser.add_argument('--debug', action='store_const', const=True, default=False)
```

**Count Occurrences**:
```python
parser.add_argument('-v', action='count', default=0)
# catena4j command -vvv
# args.v = 3
```

## Integration with Command Dispatcher

The CLI system integrates with the command dispatcher:

```
User Input: catena4j checkout -p Chart -v 15b1 -w ./work
         ↓
RootArgumentParser.parse_args()
         ↓
args = Namespace(
    command='checkout',  # Stored in dest from config
    p='Chart',
    v='15b1',
    w='./work'
)
         ↓
start_cli() extracts 'command'
         ↓
dispatcher.run('checkout', args, cli=True)
         ↓
checkout.run(ExecutionContext(args, CLI, dispatcher))
```

## Configuration

CLI behavior is configured in `config.py`:

```python
cli_program = 'catena4j'           # Program name
cli_description = None             # Program description
cli_usage = None                   # Custom usage string
cli_command_dest = '\0command'     # Internal attribute name
```

**Why `\0command`?**
- Null character prefix avoids conflicts with user arguments
- Ensures uniqueness
- Internal implementation detail

## Best Practices

### DO

✅ Use `_create_command()` for consistency
✅ Set `__add_arguments_help__` appropriately
✅ Provide clear help text for all arguments
✅ Use `add_help=False` and implement help manually if needed
✅ Use appropriate formatters for different content types
✅ Create mutually exclusive groups for conflicting options

### DON'T

❌ Create parsers directly without manager
❌ Forget to call `initialize()` in command modules
❌ Use generic argument names like `-f` or `-o` without context
❌ Overload parsers with too many arguments
❌ Forget to document custom arguments
❌ Use positional arguments when named arguments are clearer

## Examples

### Simple Command

```python
def initialize():
    global _parser
    _parser = _create_command('simple', help='Simple command')
    _parser.add_argument('name', help='Name to greet')

def run(context):
    print(f"Hello, {context.args.name}!")
```

### Complex Command with Options

```python
def initialize():
    global _parser
    _parser = _create_command('complex',
                              help='Complex command',
                              description='A more complex command example',
                              add_help=False)
    
    _parser.add_argument('-i', '--input', required=True,
                         help='Input file')
    _parser.add_argument('-o', '--output', required=False,
                         help='Output file (default: stdout)')
    _parser.add_argument('-f', '--format', choices=['json', 'csv'],
                         default='json',
                         help='Output format')
    _parser.add_argument('--verbose', action='store_true',
                         help='Verbose output')
    
    _parser.__add_arguments_help__ = True

def run(context):
    args = context.args
    # Read input
    data = read_data(args.input)
    # Format output
    formatted = format_data(data, args.format)
    # Write output
    if args.output:
        write_file(args.output, formatted)
    else:
        print(formatted)
```

### Command with Subgroups

```python
def initialize():
    global _parser
    _parser = _create_command('process', add_help=False)
    
    # Input/output options
    io_group = _parser.add_argument_group('I/O Options')
    io_group.add_argument('-i', required=True)
    io_group.add_argument('-o', required=False)
    
    # Processing options
    proc_group = _parser.add_argument_group('Processing Options')
    proc_group.add_argument('--threads', type=int, default=1)
    proc_group.add_argument('--batch-size', type=int, default=100)
    
    # Mode selection (mutually exclusive)
    mode_group = _parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--fast', action='store_true')
    mode_group.add_argument('--accurate', action='store_true')
    
    _parser.__add_arguments_help__ = True
```

## Troubleshooting

### Issue: Arguments Not Recognized

**Symptom**: `error: unrecognized arguments: -x`

**Solution**: Ensure argument is added in `initialize()` function and that `initialize()` is called during bootstrap.

### Issue: Help Not Showing Arguments

**Symptom**: `catena4j command -h` doesn't show argument details

**Solution**: Set `parser.__add_arguments_help__ = True`

### Issue: Conflicting Arguments

**Symptom**: Two arguments seem to interfere with each other

**Solution**: Use mutually exclusive groups or check for conflicts in command logic

### Issue: Command Not Found

**Symptom**: `error: invalid choice: 'mycommand'`

**Solution**: Ensure command is registered in `bootstrap.initialize_commands()`

## See Also

- [API Reference](../API.md) - Command dispatcher and execution context
- [Commands Guide](../commands/README.md) - Implementing commands
- [Architecture](../ARCHITECTURE.md) - System design overview
