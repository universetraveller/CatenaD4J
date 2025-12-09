import subprocess
import traceback
import itertools
import time
import math
import javalang
import re
import os

def runCommand(cmd, encoding='utf-8', cwd=None, timeout=None):
    try:
        finished = subprocess.run(cmd, capture_output=True, cwd=cwd, timeout=timeout)
        finished.check_returncode()
        return True, finished.stdout.decode(encoding), finished.stderr.decode(encoding)
    except subprocess.CalledProcessError:
        return False, finished.stdout.decode(encoding), finished.stderr.decode(encoding)
    except subprocess.TimeoutExpired:
        return False, '{} time out after {} seconds'.format(cmd, timeout), '{} time out after {} seconds'.format(cmd, timeout)
class SimpleLogger:
    def __init__(self, filename):
        self.fileInst = open(filename, 'a')
    def log(self, obj):
        self.fileInst.write('{}\n'.format(obj))
        self.fileInst.flush()
    def end(self):
        self.fileInst.close()
class Failure:
    def __init__(self, number, names, details, tag=None):
        self.number = number
        self.names = names
        self.details = details
        self.tag = tag
    def format(self, formatter='json'):
        if formatter == 'json':
            return self.toJson()
    def toJson(self):
        root = {}
        root['failing_test_num'] = self.number
        root['failing_tests'] = self.names
        root['stack_trace'] = self.details
        return root
D4J_TEST = 0
CMDFAIL = 1
def cleanup(path, build_dir):
    for i in build_dir:
        runCommand(['rm', '-rf', '{}/{}'.format(path, i)])
def get_failing_tests(path, build_dir:list, timeout=900):
    start_time = time.time()
    result = runCommand(['defects4j', 'test', '-w', '{}'.format(path)], timeout=timeout)
    used_time = 'Finished in {:.2f} seconds'.format(time.time() - start_time)
    if result[0]:
        output = result[1].splitlines()
        names = []
        for line in output:
            if 'Failing tests:' in line:
                num = int(line.replace('Failing tests:', '').strip())
            else:
                names.append(line[line.find('-')+1:].strip())
        #with open('{}/failing_tests'.format(path), 'r') as f:
        #    details = f.read()
        details = used_time
        cleanup(path, build_dir)
        return Failure(num, names, details, D4J_TEST)
    else:
        cleanup(path, build_dir)
        return Failure(-100, [], result[2], CMDFAIL)
def math_log2(n):
    return math.log2(n)
def iter_getFixPattern(num, _max):
    final = [(False,)*num]
    _round = 1
    generator =  itertools.combinations(range(num), _round)
    while len(final) < _max:
        try:
            get = next(generator)
        except StopIteration:
            _round += 1
            generator =  itertools.combinations(range(num), _round)
        else:
            base = [False]*num
            for i in get:
                base[i] = True
            final.append(tuple(base))
    return final
def getFixPattern(num, _max):
    if num > math_log2(_max):
        return iter_getFixPattern(num, _max)
    fix = [False, True]
    raw = list(itertools.product(fix, repeat=num))
    raw.sort(key=lambda x : x.count(True))
    return raw
def getLabel(l):
    label = ''
    for i in l:
        if i:
            label += '1'
        else:
            label += '0'
    return label
backup_encoding = ['utf-8', 'latin-1']
def validate_encoding(filename):
    for enc in backup_encoding:
        try:
            with open(filename, 'r', encoding=enc) as f:
                f = f.read()
            return enc
        except:
            continue
    return backup_encoding[0]
def get_method_info(source_code, target_line):
    tree = javalang.parse.parse(source_code)
    closest_method = None
    closest_start = -1

    for path, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            if node.position:
                start_line = node.position.line
                if start_line <= target_line and start_line > closest_start:
                    closest_start = start_line
                    closest_method = node

    if closest_method:
        return closest_method.name, closest_start

    return None

def get_catena_id_from_method(source_code):
    match = re.search(r'(public|private|protected)?\s*(?:\s*(?:static|final|synchronized))*\s*(?:<[\w\s,?<>]+>\s*)?([\w\<\>\[\]\?]+\s+)?'
                      r'[\w]+[$_]catena_(\d+)\s*\(.*?\)', source_code)
    return match.group(3), match.start(3)

def get_qualified_class_name(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    tree = javalang.parse.parse(source)
    package_name = ''
    if tree.package:
        package_name = tree.package.name + '.'
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    return "{}{}".format(package_name, file_name)
