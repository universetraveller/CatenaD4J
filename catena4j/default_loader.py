from . import config
from . import util
from . import ProjectManager
import json

class DefaultPathLoader:
    def __init__(self):
        self.root = config.root
        self.path = '{}/projects/{}/{}/{}.{}'
    def construct_path(self, proj, bid, cid, attr):
        return self.path.format(self.root, proj, bid, cid, attr)
    def get_attr(self, proj, bid, cid, attr):
        with open(self.construct_path(proj, bid, cid, attr), 'r') as f:
            f = f.read()
        return f
    def parse_test_patch(self, block):
        __paths = set()
        __edits = []
        for __primitive_test_name in block:
            __child_block = block[__primitive_test_name]
            __path_name = __child_block['file_path']
            _begin_line_no = __child_block['begin_line_no']
            _range_to_replace = __child_block['end_line_no'] - _begin_line_no + 1
            _code_to_replace = '\n'.join(__child_block['to'])
            __paths.add(__path_name)
            _line_edit = ProjectManager.EditTypes.createLineReplace(_begin_line_no, _code_to_replace, _range_to_replace)
            __edits.append(ProjectManager.FileManager.FileEdit(__path_name, _line_edit))
        return __paths, __edits
    def parse_line_edit(self, _type, _block):
        if _type == 'insert':
            return ProjectManager.EditTypes.createLineInsert(_block['next_line_no'], _block['replaced_with'])
        elif _type == 'delete':
            return ProjectManager.EditTypes.createLineDelete(_block['from_line_no'], _block['to_line_no']-_block['from_line_no']+1)
        elif _type == 'replace':
            return ProjectManager.EditTypes.createLineReplace(_block['from_line_no'], _block['replaced_with'], _block['to_line_no']-_block['from_line_no']+1)
        else:
            raise util.C4JInsideError(f'Unknown patch type {_type}')
    def parse_src_patch(self, block):
        __paths = set()
        __edits = []
        for patch_block in block['patch']:
            __file_path = patch_block['file_name']
            __paths.add(__file_path)
            __edit_type = patch_block['patch_type']
            __edits.append(ProjectManager.FileManager.FileEdit(__file_path, self.parse_line_edit(__edit_type, patch_block)))
        return __paths, __edits
    def load(self, proj, bid, cid, buggy, wd):
        # checkout buggy version
        if util.invoke_d4j_direct('checkout', p=proj, v=f'{bid}b', w=wd):
            util.printc('Exit checkout tasks')
            raise util.C4JInsideError(f'Failed to check out {bid}b')
        # apply test patch
        test_manager = ProjectManager.FileManager.FileManager(wd, ProjectManager.FileTypes.EditCacheFile)
        test_patch = json.loads(self.get_attr(proj, bid, cid, 'test.patch'))
        _test_files, _test_edits = self.parse_test_patch(test_patch)
        util.auto_task_printc(util.FOR_EACH(_test_files, test_manager.trace_file), 'Tracing test files')
        util.auto_task_printc(util.FOR_EACH(_test_edits, test_manager.apply_edit), 'Applying test patch')
        util.auto_task_printc(util.INVOKE0(test_manager.write_to_file), 'Write to file')
        util.task_printc('Buggy program version checked out for {}-{}{}{}'.format(proj, bid, 'b' if buggy else 'f', cid)).finish()
        if not buggy:
            self.fix(proj, bid, cid, wd, buggy=False)
    def fix(self, proj, bid, cid, wd, buggy=False):
        src_patch = json.loads(self.get_attr(proj, bid, cid, 'src.patch'))
        _src_files, _src_edits = self.parse_src_patch(src_patch)
        self.load_fixed_done(_src_files, _src_edits, wd)
        util.task_printc('Fixed program version checked out for {}-{}{}{}'.format(proj, bid, 'b' if buggy else 'f', cid)).finish()
    def load_fixed_done(self, files, patches, wd):
        file_manager = ProjectManager.FileManager.FileManager(wd, ProjectManager.FileTypes.EditCacheFile)
        util.auto_task_printc(util.FOR_EACH(files, file_manager.trace_file), 'Tracing src files')
        util.auto_task_printc(util.FOR_EACH(patches, file_manager.apply_edit), 'Applying src patch')
        util.auto_task_printc(util.INVOKE0(file_manager.write_to_file), 'Write to file')
