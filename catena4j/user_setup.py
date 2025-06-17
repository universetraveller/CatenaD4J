'''
    This module is used to override the behaviors of bootstrap or do some post
    initialization setup while keep bootstrap.py clean at the same time.
'''
'''
    Example 1: Add new commands or loaders directly

    from .commands import register
    from .commands import custom_command
    register('custom_command_name', custom_command.run)

    from .loaders import register_loader
    from .loaders import custom_loader
    register_loader('custom_loader_name', custom_loader)
'''
'''
    Example 2: Change the entry point

    from bootstrap import register_entry_point

    def custom_start():
        print('hello')

    register_entry_point(custom_start)
'''
'''
    Example 3: Post initialization behaviours

    from .env import get_system_env
    system_env = get_system_env()
    print(f"Current workdir is {system_env.workdir}")
'''

