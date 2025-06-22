from .project_loader import ProjectLoader

class JacksonDatabindLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }