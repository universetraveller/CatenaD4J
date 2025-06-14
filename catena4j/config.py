'''
    Configurations defined here would override properties
    from the system env in the system context

    Scope example:
        # config.py
        cli = argparse.Namespace()
        cli.usage = None

        # test.py
        import env
        assert env.get_system_config().cli.usage is None
'''
cli_program = 'catena4j'
cli_description = None
cli_usage = None
cli_command_dest = '\0command'
rel_cache_dir = '.cache'