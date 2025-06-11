from . import entries
def test(args):
    print(args)
entries.register_command('testcmd', test)
