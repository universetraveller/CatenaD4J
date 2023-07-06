import unittest
import sys
sys.path.append('../..')
import ProjectManager.FileManager as FileManager
import ProjectManager.FileTypes as FileTypes
import ProjectManager.EditTypes as EditTypes
class testFileManager(unittest.TestCase):
    def test_create(self):
        fm = FileManager.FileManager('./', FileTypes.EditCacheFile)
        fm.trace_file('./testfile.java', 'alias1')
        fm.trace_file('./util.py', 'alias2')
        self.assertIsInstance(fm.get('alias2'), FileTypes.EditCacheFile)
        self.assertIsInstance(fm.get('./util.py'), FileTypes.EditCacheFile)
        self.assertIsInstance(fm.get('.//./util.py'), FileTypes.EditCacheFile)
        fm.remove('alias2')
        test = False
        try:
            fm.get('alias2')
        except KeyError:
            test = True
        self.assertTrue(test)
        test = False
        try:
            fm.trace_file('./util.py', 'alias1')
        except FileManager.NameConflictError:
            test = True
        self.assertTrue(test)
    def test_findLastMatch(self):
        func = FileManager.findLastMatch
        l1 = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        l2 = [0, 1, 2, 3]
        l3 = [0, 1, 2, 5]
        l4 = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        l5 = []
        l6 = [0]
        l7 = [1]
        self.assertEqual(func(l1, l2), 3)
        self.assertEqual(func(l1, l3), 2)
        self.assertEqual(func(l1, l4), 8)
        self.assertEqual(func(l1, l5), None)
        self.assertEqual(func(l1, l6), 0)
        self.assertEqual(func(l1, l7), None)
    def test_reset(self):
        fm = FileManager.FileManager('.', FileTypes.EditCacheFile)
        fm.trace_file('testfile.java', 'f1')
        fm.trace_file('util.py', 'f2')
        edit = FileManager.FileEdit('testfile.java', EditTypes.createLineDelete(1))
        code = fm.get('f1').toString()
        self.assertEqual(code, fm.get('testfile.java').toString())
        fm.apply_edit(edit)
        self.assertNotEqual(code, fm.get('testfile.java').toString())
        fm.reset()
        self.assertEqual(code, fm.get('testfile.java').toString())
    def test_commit(self):
        fm = FileManager.FileManager('.', FileTypes.EditCacheFile)
        fm.trace_file('testfile.java', 'f1')
        fm.trace_file('util.py', 'f2')
        edit = FileManager.FileEdit('testfile.java', EditTypes.createLineDelete(1))
        code = fm.get('f1').toString()
        self.assertEqual(code, fm.get('testfile.java').toString())
        fm.apply_edit(edit)
        self.assertNotEqual(code, fm.get('testfile.java').toString())
        fm.commit('message')
        self.assertTrue(fm.commits)
        self.assertEqual(fm.commits[1].commit_id, 1)
        fm.apply_edit(edit)
        fm.commit('message1')
        self.assertEqual(fm.commits[2].message, 'message1')
    def test_checkout(self):
        fm = FileManager.FileManager('.', FileTypes.EditCacheFile)
        fm.trace_file('testfile.java', 'f1')
        fm.trace_file('util.py', 'f2')
        edit = FileManager.FileEdit('testfile.java', EditTypes.createLineDelete(1))
        code = fm.get('f1').toString()
        self.assertEqual(code, fm.get('testfile.java').toString())
        edit1 = FileManager.FileEdit('util.py', EditTypes.createLineDelete(1))
        try:
            fm.commit('message', 123)
        except FileManager.CommitFailed:
            pass
        fm.apply_edit(edit1)
        fm.commit('message', 123)
        self.assertEqual(fm.commits[123].commit_id, 123)
        fm.apply_edit(edit)
        self.assertNotEqual(code, fm.get('testfile.java').toString())
        fm.commit('message')
        self.assertTrue(fm.commits)
        self.assertEqual(fm.commits[124].commit_id, 124)
        fm.apply_edit(edit)
        fm.commit('message1')
        self.assertEqual(fm.commits[125].message, 'message1')
        self.assertNotEqual(fm.get('testfile.java').toString(), code)
        fm.checkout(123)
        self.assertEqual(fm.get('testfile.java').toString(), code)
    def test_checkout_1(self):
        fm = FileManager.FileManager('.', FileTypes.EditCacheFile)
        fm.trace_file('testfile.java', 'f1')
        fm.trace_file('util.py', 'f2')
        edit = FileManager.FileEdit('testfile.java', EditTypes.createLineDelete(1))
        code = fm.get('f1').toString()
        self.assertEqual(code, fm.get('testfile.java').toString())
        fm.apply_edit(edit)
        self.assertNotEqual(code, fm.get('testfile.java').toString())
        fm.commit('message')
        self.assertTrue(fm.commits)
        self.assertEqual(fm.commits[1].commit_id, 1)
        fm.apply_edit(edit)
        fm.commit('message1')
        self.assertEqual(fm.commits[2].message, 'message1')
        self.assertNotEqual(fm.get('testfile.java').toString(), code)
        fm.checkout(0)
        self.assertEqual(fm.get('testfile.java').toString(), code)
if __name__ == '__main__':
    unittest.main()
