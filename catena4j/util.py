from argparse import Namespace

def get_constant_class(name='Constant', namespace={}, slots=(), bases=()):
    '''
        Get a constant class whose instances' attributes outside
        slots are not allowed to modify

        Internal attributes could be accessed using __class__
    '''
    namespace['__slots__'] = slots
    return type(name, bases, namespace)

def build_args(**kwargs):
    '''
        Tool function to create args object
    '''
    return Namespace(**kwargs)
