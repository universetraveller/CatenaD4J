import argparse
from v1.backend import print_help, is_help_cmd, d4j_backend, c4j_backend
from v1 import config
from v1 import util
from v1 import entries
def do_nothing(*args, **kwargs):
    pass

def check_help():
    if is_help_cmd():
        print_help()
        exit(1)

def init_parser():
    parser = argparse.ArgumentParser(add_help=False)
    if not config.CONFIG_DEBUG:
        setattr(parser, 'error', do_nothing)
    return parser

def send_args(args):
    if not args.command in config.d4j_cmds + entries.names():
        print_help()
        return 1
    else:
        c4j_backend(args)
        return 0

def process_argument_error():
    import sys
    args = sys.argv
    if args[1] in config.d4j_cmds + entries.names():
        # print root cause
        print(sys.exc_info()[1])
        # try to print command usage
        _args = argparse.Namespace()
        _args.command = args[1]
        c4j_backend(_args)
    else:
        print_help()
    exit(1)

def main(parser):
    try:
        args = parser.parse_args()
        exit(send_args(args))
    except util.C4JInsideError:
        # Inside error should not be ignored for debugging
        raise
    except argparse.ArgumentError:
        process_argument_error()
    except Exception:
        # If use 'except:' there it will catch BaseException like SystemExit
        if config.CONFIG_DEBUG:
            raise
        d4j_backend()
