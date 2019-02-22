""" Unit tests for handler
"""

# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
import requests
from handler import *
from py_cert import *


class TesthandlerCertToDict(unittest.TestCase):
    def setUp(self):
        CA_subj = {'Country':u'PL', 'State':u'Mazowieckie', 'Locality':u'Warszawa',
                   'Organization':u'NCBJ', 'OU':u'Student', 'CN':u'CA'}
        test_subj = {'Country':u'PL', 'State':u'Mazowieckie', 'Locality':u'Warszawa',
                     'Organization':u'NCBJ', 'OU':u'Student', 'CN':u'test'}
        key_CA, CA_subj, CA_crt = create_CA('tc/CAcert.pem', 'tc/CAkey.pem', CA_subj)
        test_key, test_crt = create_test_cert('tc/user.crt', 'tc/user.key', key_CA, CA_subj, test_subj)
        test_key, test_crt = create_test_cert('tc/server.crt', 'tc/server.key', key_CA, CA_subj, test_subj)
        app = make_app()
        ssl_ctx = generate_ssl_context('../tc/')
        http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
        http_server.listen(1027)
        tornado.ioloop.IOLoop.current().start()
        URL = 'https://localhost:1027/json'
    def tearDown(self):
        pass

    def test_success(self):
        certDir = '../tc/'
        client_cert = os.path.join(certDir+'user.crt')
        client_key = os.path.join(certDir+'user.key')
        CAcert = os.path.join(certDir+'CAcert.pem'
        r1 = requests.get(URL, cert=(client_cert, client_key), verify=CAcert)
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
