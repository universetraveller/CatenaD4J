from .project_loader import ProjectLoader

class ChartLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'source',
            'test': 'tests'
        }