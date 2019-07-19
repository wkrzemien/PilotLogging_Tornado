import unittest
from code import *

class Test_get_DN(unittest.TestCase):
    def test_success(self):
        res = get_DN('Pilot')
        self.assertTrue(res['OK'])
    def test_fail(self):
        res = get_DN('Some_ Group')
        self.assertFalse(res['OK'])
    def test_bad_input(self):
        res = get_DN(123)
        self.assertFalse(res['OK'])

if __name__=='__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test_get_DN)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
