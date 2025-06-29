import sys
sys.path.append('../..')
import ProjectManager.FileTypes as FileTypes
from ProjectManager.EditTypes import LineEdit, MetaLineEdit
from ProjectManager.constants import *
import unittest
class testEditTypes(unittest.TestCase):
    def test_edits_reusing(self):
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(REPLACE, 3, -1, 'test\n', 2)
        ans = '''public class testfile{
test
}
}
'''
        test.apply_edit(edit)
        test = FileTypes.EditCacheFile('./testfile.java')
        test.apply_edit(edit)
        self.assertEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        test.commit()
        self.assertEqual(test.uncommitted, [])
        self.assertEqual(test.toString(), ans)
if __name__ == '__main__':
    unittest.main()
