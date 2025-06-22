from .project_loader import ProjectLoader

class JacksonXmlLoader(ProjectLoader):
    def determine_layout(self):
        return {
            'src': 'src/main/java',
            'test': 'src/test/java'
        }