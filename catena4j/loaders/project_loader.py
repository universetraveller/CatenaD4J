from .loader import ContextAwareLoader
from pathlib import Path
from ..c4jutil import get_property, apply_json_patch
from ..util import read_file, toolkit_execute, Files, write_file
from ..d4jutil import fix_tests
import json

class ProjectLoader(ContextAwareLoader):
    version_control_system_class = None
    project_name = None

    def __init__(self, context):
        super().__init__(context=context)
        self._layout = None
        if self.version_control_system_class is None:
            raise NotImplementedError("Subclasses must set a version control system class")

        if self.project_name is None:
            raise NotImplementedError("Subclasses must set a project name")

    @property
    def version_control_system(self):
        if not hasattr(self, '_version_control_system'):
            self._version_control_system = self.version_control_system_class(self)
        return self._version_control_system

    def checkout_revision(self, revision_id: str, wd: str):
        '''
            Delegate the checkout tasks to a specific version control system
        '''
        return self.version_control_system.checkout_revision(revision_id, wd)
    
    def export_diff(self, a: str, b: str, output: Path=None):
        '''
            Delegate the diff tasks to a specific version control system

            a and b are both commit id

            output is an optional path, if it is not None, the diff result will be
            written to it 
        '''
        return self.version_control_system.export_diff(a, b, output)

    @property
    def src_layout(self):
        '''
            get the src directory layout of current context

            subclasses should implement method determine_src_layout
        '''
        if self._layout is None:
            self._layout = self.determine_layout()

        return self._layout['src']

    @property
    def test_layout(self):
        '''
            get the test directory layout of current context

            subclasses should implement method determine_test_layout
        '''
        if self._layout is None:
            self._layout = self.determine_layout()
        
        return self._layout['test']

    def determine_layout(self):
        '''
            Should return a dict with keys src and test,
            
            and the values mapped are the src and test directory layout
        '''
        raise NotImplementedError('This method should be implemented by subclasses')

    @property
    def repo_path(self):
        if not hasattr(self, 'rel_to_repo'):
            self.rel_to_repo = self.version_control_system_class \
                                   .format_name(self.project_name)

        return Path(self.context.d4j_home,
                    self.context.d4j_rel_repositories,
                    self.rel_to_repo)
    
    def d4j_checkout_hook(self, project: str, revision_id: str, wd: str):
        '''
            Project specific works, return a boolean indicating if there
            are file changes
        '''
        return False
    
    def get_property(self, name: str, project: str, bid: str, cid: str):
        return get_property(name, project, bid, cid, self.context)
    
    def load_buggy_version(self, project: str, bid: str, cid: str, wd: str):
        files = Files(wd)
        test_patch = json.loads(self.get_property('test.patch', project, bid, cid))
        for hunk in test_patch:
            apply_json_patch(test_patch[hunk], files)
        
        files.write_back()

    def load_fixed_version(self, project: str, bid: str, cid: str, wd: str):
        files = Files(wd)
        src_patch = json.loads(self.get_property('src.patch', project, bid, cid))['patch']
        for hunk in src_patch:
            apply_json_patch(hunk, files)
        
        files.write_back()
    
    def toolkit_execute(self,
                        target: str,
                        project: str,
                        wd: str,
                        *,
                        task_printer=None,
                        xml_attr: str='c4j_rel_project_compile_xml',
                        main_attr: str='c4j_toolkit_execute_main',
                        java_options=()):
        context = self.context
        xml = Path(context.c4j_home,
                   getattr(context, xml_attr).format(project=project))
        args = (str(xml), target) if isinstance(target, str) else (str(xml), *target)
        return toolkit_execute(getattr(context, main_attr),
                               wd,
                               context,
                               java_options=java_options,
                               args=args,
                               task_printer=task_printer)
    
    def fix_tests(self,
                  project,
                  bid,
                  wd,
                  is_buggy,
                  *,
                  revision_id=None,
                  _except=set(),
                  verbose=False):
        '''
            Projects like Math need specific fix_tests method
        '''
        return fix_tests(project,
                         bid,
                         wd,
                         is_buggy,
                         self.context,
                         loader=self,
                         revision_id=revision_id,
                         _except=_except,
                         verbose=verbose)