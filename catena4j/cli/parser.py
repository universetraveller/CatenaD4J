from argparse import ArgumentParser, HelpFormatter, _SubParsersAction
from sys import stderr

try:
    from gettext import gettext as _
except ImportError:
    def _(message):
        return message

class RootArgumentParser(ArgumentParser):
    '''
        Override some default behaviours for better experience
    '''
    def error(self, message: str):
        self._print_message(message + '\n', stderr)
        self.print_help(stderr)
        self.exit(2)

    def _get_current_subparser(self, args):
        if self._subparsers is None:
            return self

        for action in self._subparsers._group_actions:
            if not isinstance(action, _SubParsersAction):
                continue

            parsed = getattr(args, action.dest, None)
            if parsed:
                return action.choices.get(parsed, self)
        
        return self

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)

        if argv:
            parser = self._get_current_subparser(args)
            msg = _('unrecognized arguments: %s')
            parser.error(msg % ' '.join(argv))

        return args

class RootHelpFormatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if actions:
            # get cleaner output for case that lots of subcommands exist
            usage = _('%(prog)s <command> [option]')

        args = usage, actions, groups, prefix
        self._add_item(self._format_usage, args)

    def _format_action(self, action):
        # remove action_header to make the output cleaner
        parts = []

        for subaction in self._iter_indented_subactions(action):
            parts.append(super()._format_action(subaction))

        return self._join_parts(parts)

class LeafArgumentParser(RootArgumentParser):
    def format_help(self):
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        if getattr(self, '__add_arguments_help__', False):
            for action_group in self._action_groups:
                formatter.start_section(action_group.title)
                formatter.add_text(action_group.description)
                for action in action_group._group_actions:
                    if action.help:
                        formatter.add_argument(action)
                formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()