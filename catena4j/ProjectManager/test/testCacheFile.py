import sys
sys.path.append('../..')
import ProjectManager.FileTypes as FileTypes
from ProjectManager.EditTypes import LineEdit, MetaLineEdit
from ProjectManager.constants import *
import unittest

class testEditCacheLine(unittest.TestCase):
    def test_insert(self):
        line = FileTypes.EditCacheLine(1, 'test')
        edit = MetaLineEdit(INSERT, back=False, cont='before')
        line.apply_edit(edit)
        self.assertEqual(line.prefix.strip(), 'before')
        edit = MetaLineEdit(INSERT, back=True, cont='after')
        line.apply_edit(edit)
        self.assertEqual(line.suffix.strip(), 'after')
        self.assertEqual(line.cont.strip(), 'test')
        line.commit()
        self.assertEqual(line.cont, 'before test after')
        self.assertEqual(line.edited, False)
    def test_delete(self):
        line = FileTypes.EditCacheLine(1, 'test')
        edit = MetaLineEdit(DELETE)
        line.apply_edit(edit)
        self.assertEqual(line.cont, '')
    def test_replace(self):
        line = FileTypes.EditCacheLine(1, 'test')
        edit = MetaLineEdit(REPLACE, cont='abc')
        line.apply_edit(edit)
        self.assertEqual(line.cont, 'abc')
    def test_two_edits(self):
        line = FileTypes.EditCacheLine(1, 'test')
        edit = MetaLineEdit(REPLACE, cont='abc')
        line.apply_edit(edit)
        edit = MetaLineEdit(DELETE)
        line.apply_edit(edit)
        edit = MetaLineEdit(INSERT, back=False, cont='before')
        line.apply_edit(edit)
        self.assertEqual(line.cont, '')
        self.assertEqual(line.prefix.strip(), 'before')
        line.commit()
        self.assertEqual(line.cont.strip(), 'before')
class testEditCacheFile(unittest.TestCase):
    def test_create(self):
        test = FileTypes.EditCacheFile('./testfile.java')
        tag = True
        if len(test.content) == 0:
            tag = False
        self.assertTrue(tag)
        for i in test.content:
            if i.cont.strip() == '':
                tag = False
        self.assertTrue(tag)
    def test_apply_edit(self):
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(REPLACE, 3, -1, 'test\n', 2)
        ans = '''public class testfile{
test
}
}
'''
        test.apply_edit(edit)
        self.assertEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        test.commit()
        self.assertEqual(test.uncommitted, [])
        self.assertEqual(test.toString(), ans)
    def test_apply_edit_1(self):
        ans = '''public class testfile{
public static void main(String[] args){
System.out.println("Hello world.");
}
}
'''
        ans = '''public class testfile{
}
}
'''
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(DELETE, 3, -1, _range=2)
        test.apply_edit(edit)
        self.assertEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        test.commit()
        self.assertEqual(test.uncommitted, [])
        self.assertEqual(test.toString(), ans)
    def test_apply_edit_2(self):
        ans = '''public class testfile{
test public static void main(String[] args){
System.out.println("Hello world.");
}
}
'''
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(INSERT_BEFORE, 3, -1, 'test')
        test.apply_edit(edit)
        self.assertEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        self.assertNotEqual(len(test.uncommitted), 0)
        test.commit()
        self.assertEqual(len(test.uncommitted), 0)
        self.assertEqual(test.toString(), ans)
    def test_apply_edit_3(self):
        ans = '''public class testfile{
public static void main(String[] args){
 testSystem.out.println("Hello world.");
}
}
'''
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(INSERT_AFTER, 3, -1, 'test')
        test.apply_edit(edit)
        self.assertEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        self.assertNotEqual(len(test.uncommitted), 0)
        test.commit()
        self.assertEqual(len(test.uncommitted), 0)
        self.assertEqual(test.toString(), ans)
    def test_apply_edit_4(self):
        ans = '''public class testfile{
public static void main(String[] args){
System.out.println("Hello world.");
}
}
'''
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(INSERT_AFTER, 3, -1, 'test')
        test.apply_edit(edit)
        self.assertTrue(test.edited)
        self.assertNotEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        self.assertNotEqual(len(test.uncommitted), 0)
        self.assertTrue(test.abortEdits())
        self.assertFalse(test.edited)
        self.assertEqual(len(test.uncommitted), 0)
        self.assertEqual(test.toString(), ans)
    def test_apply_edit_5(self):
        ans = '''public class testfile{
public static void main(String[] args){
System.out.println("Hello world.");
}
}
'''
        test = FileTypes.EditCacheFile('./testfile.java')
        edit = LineEdit(INSERT_AFTER, 3, -1, 'test')
        test.apply_edit(edit)
        self.assertTrue(test.edited)
        self.assertNotEqual(test.toString(), ans)
        self.assertNotEqual(test.uncommitted, [])
        self.assertNotEqual(len(test.uncommitted), 0)
        diff = test.commit()
        self.assertTrue(diff.restore(test))
        self.assertFalse(test.edited)
        self.assertEqual(len(test.uncommitted), 0)
        self.assertEqual(test.toString(), ans)
        self.assertTrue(diff.apply(test))
        self.assertFalse(test.edited)
        self.assertEqual(len(test.uncommitted), 0)
        self.assertNotEqual(test.toString(), ans)

if __name__ == '__main__':
    unittest.main()
