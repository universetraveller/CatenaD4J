from unidiff import PatchSet
a = PatchSet.from_filename('./136.src.patch')
def printA(a, b):
    print('{}: {}'.format(b, getattr(a, b)))
for i in a:
    for j in i:
        for k in j:
            print('Line---')
            printA(k, 'source_line_no')
            printA(k, 'target_line_no')
            printA(k, 'diff_line_no')
            printA(k, 'line_type')
            print(k.is_added)
            print(k.is_removed)
            print(k.is_context)
            printA(k, 'value')
            if '\n' in getattr(k, 'value'):
                print('contains return')
