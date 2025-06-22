from .project_loader import ProjectLoader

class JsoupLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }