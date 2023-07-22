from . import util
from . import checkout
from . import export
from . import reset

def no_impl(*arglist, **argmap):
    raise util.C4JInsideError("The method is not implemented")

__entry_map = {
# Begin
# Register commands with method implementation there or use function register_command()
        "checkout" : checkout.CHECKOUT,
        "export" : export.EXPORT,
        "reset" : reset.RESET,
        "ver" : no_impl,
        "info" : no_impl
# End
        }

def invoke(name, args):
    if not name in __entry_map:
        util.printc('Unknown command {}'.format(name))
        return
    __entry_map[name](args)

def register_command(name, impl):
    __entry_map[name] = impl
def remove_command(name):
    __entry_map.pop(name)

def __names():
    for i in __entry_map:
        yield i
def names():
    return list(__names())
