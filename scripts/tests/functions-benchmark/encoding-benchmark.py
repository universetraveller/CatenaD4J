from benchmark import test1
import tempfile
utf8_bytes = ("€" * 10000).encode("utf-8")
common_bytes = ("a" * 10000).encode("utf-8")
latin1_bytes = bytes([0xFF] * 10000)

def create_temp_file(byte_data, suffix=".txt"):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp.write(byte_data)
    temp.flush()
    temp.close()
    return temp.name

# Write both test files
utf8_file = create_temp_file(utf8_bytes)
latin1_file = create_temp_file(latin1_bytes)
common_file = create_temp_file(common_bytes)

encodings = ('utf-8', 'latin-1', 'cp1252', 'utf-16', 'utf-32')
def open_t(a):
    for enc in encodings:
        try:
            with open(a, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

def open_t1(a):
    try:
        with open(a) as f:
            return f.read()
    except UnicodeDecodeError:
        with open(a, encoding='latin-1') as f:
            return f.read()

def open_s(a):
    with open(a, encoding='latin-1') as f:
        return f.read()

test1(open_t, 10000, latin1_file)
test1(open_s, 10000, latin1_file)
test1(open_t1, 10000, latin1_file)
test1(open_t, 10000, common_file)
test1(open_s, 10000, common_file)
test1(open_t1, 10000, common_file)
