from argparse import ArgumentParser, HelpFormatter
from sys import stdout, stderr

class RootArgumentParser(ArgumentParser):
    '''
        Override some default behaviours for better experience
    '''
    def error(self, message: str):
        self._print_message(f'{message}\n', stderr)
        self.print_help(stderr)
        self.exit(2)

class RootHelpFormatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if actions:
            # get cleaner output for case that lots of subcommands exist
            usage = '%(prog)s <command> [option]'

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
        # remove arguments to make the output cleaner
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()