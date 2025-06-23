from .project_loader import ProjectLoader
from . import LoaderError
from ..util import read_file
import re
from pathlib import Path

# with lazy import the overhead of compilation could be minimal
_layout_pattern_1 = {
    'src': re.compile(r'<property\s+name="source\.home"\s+value="([^"]+)"\s*/?>'),
    'test': re.compile(r'<property\s+name="test\.home"\s+value="([^"]+)"\s*/?>')
}

_layout_pattern_2 = {
    'src': re.compile(r'<sourceDirectory>([^<]+)</sourceDirectory>'),
    'test': re.compile(r'<unitTestSourceDirectory>([^<]+)</unitTestSourceDirectory>')
}

class MathLoader(ProjectLoader):
    def _search_layout(self, version):
        if version == 1:
            file = 'build.xml'
            layout_pattern = _layout_pattern_1
        elif version == 2:
            file = 'project.xml'
            layout_pattern = _layout_pattern_2
        else:
            raise LoaderError(f'Unknown layout for working directory: {self.context.cwd}')

        props = read_file(Path(self.context.cwd, file))

        if props is None:
            return None

        src_layout_pattern = layout_pattern['src']
        test_layout_pattern = layout_pattern['test']

        layout = {}

        for line in props.splitlines():
            line = line.strip()

            src = src_layout_pattern.match(line)
            if src:
                layout['src'] = src.group(1).strip()
                continue

            test = test_layout_pattern.match(line)
            if test:
                layout['test'] = test.group(1).strip()
                continue

        if 'src' in layout and 'test' in layout:
            return layout

        return None

    def determine_layout(self):
        layout = self._search_layout(1) or self._search_layout(2)

        if layout is None:
            raise LoaderError(f'Unknown layout for working directory: {self.context.cwd}')
        
        return layout