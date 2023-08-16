def get_lst(lst, idx, num):
    return lst[idx:idx+num]
def get_lst_log(lst, idx, num):
    pre = get_lst(lst, idx, num)
    return list(map(lambda x:x.strip(), pre))
def get_failing_tests(lst, pat):
    idx = 0
    while not lst[idx] == f'pattern: {pat}':
        idx += 1
    idx += 1
    while idx < len(lst):
        line = lst[idx]
        if not line.startswith('Failing tests:'):
            idx += 1
        else:
            num = int(line.replace('Failing tests:', '').strip())
            return get_lst_log(lst, idx+1, num)
def get_hunk_num(log):
    for i in log:
        if i.startswith('num_of_hunks'):
            return int(i.replace('num_of_hunks', '').strip())
def read_log(file_name):
    with open(file_name, 'r') as f:
        lst = f.read().splitlines()
    return lst
def test_get_failing_tests():
    lst = read_log('./working/Chart_14/log')
    assert get_failing_tests(lst, '0001') == ['org.jfree.chart.plot.junit.CategoryPlotTests::testRemoveRangeMarker', 'org.jfree.chart.plot.junit.CategoryPlotTests::testRemoveDomainMarker', 'org.jfree.chart.plot.junit.XYPlotTests::testRemoveDomainMarker']
if __name__ == '__main__':
    test_get_failing_tests()
