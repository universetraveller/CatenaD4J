from benchmark import test1
import re
import random
import string

def generate_test_text(old_list, total_len=1_000_000):
    """Generate a large random string with all old_list entries inserted once."""
    # Fill with random lowercase characters
    chunks = ["".join(random.choices(string.ascii_lowercase + " ", k=total_len - sum(len(x) for x in old_list)))]

    # Insert each old key exactly once at random positions
    for key in old_list:
        pos = random.randint(0, len(chunks))
        chunks.insert(pos, key)

    return "\n".join(chunks)

N = 10
old_list = [f"key-avuieuv={i}" for i in range(N)]
new_list = [f"val-ascqwefq={i}" for i in range(N)]

sample_keys = random.choices(old_list, k=1000)
text = generate_test_text(old_list, 15000)

def a(text):
    for old, new in zip(old_list, new_list):
        text = text.replace(old, new)
    return text

pattern = re.compile("|".join(re.escape(s) for s in old_list))
replace_dict = dict(zip(old_list, new_list))

def repl(m):
    return replace_dict[m.group(0)]

def b(text):
    return pattern.sub(repl, text)

def replace_with_regex(text):
    return pattern.sub(lambda m: replace_dict[m.group(0)], text)

assert a(text) == b(text)
assert a(text) != text
assert a(text) == b(text)
test1(a, 10000, text)
test1(b, 10000, text)
test1(replace_with_regex, 10000, text)
