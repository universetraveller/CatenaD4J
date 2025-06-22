from .project_loader import ProjectLoader

class ClosureLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'src',
            'test': 'test'
        }