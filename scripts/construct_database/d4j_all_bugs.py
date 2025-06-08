import os
import shutil
d4j_home = ''
if not d4j_home:
    d4j_home = os.path.abspath(os.path.join(shutil.which('defects4j'), '..', '..', '..'))
assert d4j_home

d4j_projs = f'{d4j_home}/framework/projects/'
all_projs = [name for name in os.listdir(d4j_projs) if os.path.isdir(os.path.join(d4j_projs, name)) and name != 'lib']
all_bugs = {}
for proj in all_projs:
    with open(f'{d4j_projs}/{proj}/active-bugs.csv') as f:
        all_bugs[proj] = [id.split(',')[0] for id in f.read().splitlines()[1:]]
d4j_props = ['classes.modified', 'classes.relevant', 'cp.compile', 'cp.test', 'dir.bin.classes', 'dir.bin.tests',  'dir.src.classes', 'dir.src.tests', 'tests.all', 'tests.relevant', 'tests.trigger']

mapping = {
    'Chart': 0,
    'Cli': 1,
    'Closure': 2,
    'Codec': 3,
    'Collections': 4,
    'Compress': 5,
    'Csv': 6,
    'Gson': 7,
    'JacksonCore': 8,
    'JacksonDatabind': 9,
    'JacksonXml': 10,
    'Jsoup': 11,
    'JxPath': 12,
    'Lang': 13,
    'Math': 14,
    'Mockito': 15,
    'Time': 16,
    'classes.modified': 17,
    'classes.relevant': 18,
    'cp.compile': 19,
    'cp.test': 20,
    'dir.bin.classes': 21,
    'dir.bin.tests': 22,
    'dir.src.classes': 23,
    'dir.src.tests': 24,
    'tests.all': 25,
    'tests.relevant': 26,
    'tests.trigger': 27
}