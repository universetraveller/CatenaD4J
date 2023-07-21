from . import default_loader


__loaders = {
        'default':default_loader.DefaultPathLoader()
        }

def get_loader(name:str):
    return __loaders[name]
def set_loader(name:str, instance):
    __loaders[name] = instance
