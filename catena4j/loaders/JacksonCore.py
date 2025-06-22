from .project_loader import ProjectLoader

class JacksonCoreLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }