from .project_loader import ProjectLoader

class GsonLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'gson/src/main/java',
            'test': 'gson/src/test/java'
        }