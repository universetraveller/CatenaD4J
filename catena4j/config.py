'''
    Configurations defined here would override properties
    from the system env in the system context

    Use specific prefix could avoid attributes being reset by
    subclasses of Context 

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
d4j_rel_ant_lib = 'major/lib/*'
c4j_rel_toolkit_lib = 'toolkit/target/toolkit.jar'
c4j_rel_d4j_properties = 'resources/defects4j.properties'
c4j_toolkit_export_main = 'io.github.universetraveller.d4j.Defects4JExport'
c4j_toolkit_execute_main = 'io.github.universetraveller.d4j.Defects4JExecute'
c4j_rel_projects = 'projects'
c4j_rel_project_export_xml = 'projects/{project}/{project}.export.xml'
c4j_rel_project_compile_xml = 'projects/{project}/{project}.compile.xml'
c4j_version_props = '.catena4j.info'
c4j_version_co_props = 'catena4j.build.properties'
d4j_version_props = '.defects4j.config'
d4j_version_co_props = 'defects4j.build.properties'
d4j_rel_projects = 'framework/projects'
d4j_rel_repositories = 'project_repos'
d4j_tag = 'D4J_{project}_{bid}_{suffix}'
rich_output = True
printer_message_length = 75
printer_padding_character = '.'