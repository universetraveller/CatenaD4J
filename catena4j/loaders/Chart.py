from pathlib import Path
from .project_loader import ProjectLoader
from ..util import Svn, apply_patch

class ChartLoader(ProjectLoader):
    version_control_system_class = Svn
    project_name = 'jfreechart'
    def determine_layout(self):
        return {
            'src': 'source',
            'test': 'tests'
        }

    def d4j_checkout_hook(self, project, revision_id, wd):
        context = self.context

        compile_errors = Path(context.d4j_home,
                              context.d4j_rel_projects,
                              project,
                              'compile-errors')

        revision_id = int(revision_id)

        changes = False
        for file in compile_errors.iterdir():
            _min, _max = map(int, file.name[:-5].rsplit('-', 2)[-2:])
            if revision_id < _min:
                continue

            if revision_id > _max:
                continue

            apply_patch(file, wd, context)

            # reaching here means there are file changes
            changes = True
        
        return changes