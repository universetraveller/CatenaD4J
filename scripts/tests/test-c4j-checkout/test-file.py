from pathlib import Path
import sys
import time

sys.path.append(f'{str(Path(__file__).parent)}/../../..')

from catena4j.util import File

f = File(Path('/tmp/bugs_static/Chart_1/source/org/jfree/chart/plot/PiePlot3D.java'))