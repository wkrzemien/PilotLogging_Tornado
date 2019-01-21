""" Unit tests for handler
"""

# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
from handler import getValidDNs


class TesthandlerCertToDict(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_success(self):
    pass


class TesthandlergetValidDNs(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_success(self):
    res = getValidDNs()
    self.assertTrue(res) 

  def test_fail(self):
    res = getValidDNs(filename='it_does_not_exist')
    self.assertFalse(res) 


if __name__ == '__main__':
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(
      TesthandlerCertToDict)
  suite.addTest(
      unittest.defaultTestLoader.loadTestsFromTestCase(TesthandlergetValidDNs))
  testResult = unittest.TextTestRunner(verbosity=2).run(suite)
