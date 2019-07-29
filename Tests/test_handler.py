""" Unit tests for handler
"""

# pylint: disable=line-too-long

import unittest
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from OpenSSL import crypto
from handler import extract_DN, getValidDNs_from_file, valid_cert, transformDNComponentsToStr
from py_cert import create_CA

class TestHandlerTransformDNComponentsToStr(unittest.TestCase):
    """ Unit tests for transformDNComponentsToStr
    """
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_success_possible_cert(self):
        """Success test for posible DN"""
        tested_dn = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        result_str = transformDNComponentsToStr(tested_dn)
        self.assertEqual(result_str, '/DC=ch/DC=cern/OU=computers/CN=lhcbi-cernvm03.cern.ch')
    def test_success_test_cert(self):
        """Success test for certificate, which is used in tests"""
        tested_cert_file = open('../testCerts/user.crt', 'r')
        tested_cert_data = tested_cert_file.read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, tested_cert_data)
        tested_dn =  transformDNComponentsToStr(cert.get_subject().get_components())
        self.assertEqual(tested_dn, '/C=PL/ST=User/L=KR/O=LocalFAke/CN=userCert/emailAddress=user@fake.pl')
    def test_raise_error_incorrect_dn(self):
        """If DN is incorrect this function must raise an ValueError"""
        tested_dn = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers', 'Ooops'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        self.assertRaises(ValueError, transformDNComponentsToStr, tested_dn)




class TestHandlerExtractDN(unittest.TestCase):
    """Tests for extract_DN function"""
    def setUp(self):
        """Creating test certificates for this tests"""
        ca_file_path = 'CA.crt'
        ca_key_path = 'CA.key'
        ca_subj_dict = {'Country':u'PL', 'State':u'Maze', 'Locality':u'KR', 'Organization':u'test', 'OU':u'unittest', 'CN':u'CA'}
        create_CA(ca_file_path, ca_key_path, ca_subj_dict, serialization.Encoding.DER)
    def tearDown(self):
        """Remove certificates"""
        os.remove('CA.crt')
        os.remove('CA.key')
    def test_success(self):
        """Check if extract dn works on created in setUp certificate"""
        ca_subj_dict = {'countryName':u'PL', 'stateOrProvinceName':u'Maze', 'localityName':u'KR', 'organizationName':u'test', 'organizationalUnitName':u'unittest', 'commonName':u'CA'}
        cert_file = open('CA.crt', 'r')
        cert_buffer = cert_file.read()
        dn = extract_DN(cert_buffer)
        self.assertEqual(dn, ca_subj_dict)
class TestHandlerGetValidDNsFromFile(unittest.TestCase):
    """Test Case for getValidDNs_from_file function"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_success(self):
        """Check if we can get valid DN from defalut file"""
        res = getValidDNs_from_file()
        self.assertTrue(res)

    def test_fail(self):
        """Check if we can get valid DN from incorrect file"""
        res = getValidDNs_from_file(filename='it_does_not_exist')
        self.assertFalse(res)
class TestHandlerValidCert(unittest.TestCase):
    """TestCase for ValidCert function"""
    def setUp(self):
        """Creating test certificates for this tests"""
        test_file_path = 'test.crt'
        test_key_path = 'test.key'
        test_subj_dict = {'Country':u'PL', 'State':u'MAZOWIECKIE', 'Locality':u'Krakow',
                        'Organization':u'Some_organization', 'OU':u'Unit', 'CN':u'test_cert'}
        create_CA(test_file_path, test_key_path, test_subj_dict, serialization.Encoding.DER)
        fail_file_path = 'fail.crt'
        fail_key_path = 'fail.key'
        fail_subj_dict = {'Country':u'PL', 'State':u'Mazowieckie', 'Locality':u'Krakow',
                        'Organization':u'Some_organization', 'OU':u'Unit', 'CN':u'fail_cert'}
        create_CA(fail_file_path, fail_key_path, fail_subj_dict, serialization.Encoding.DER)

    def tearDown(self):
        os.remove('test.crt')
        os.remove('test.key')
        os.remove('fail.crt')
        os.remove('fail.key')
    def test_success(self):
        """Checking if valid DN will return True"""
        cert_file = open('test.crt', 'r')
        cert_buffer = cert_file.read()

        valid_dn = getValidDNs_from_file()
        res = valid_cert(cert_buffer, valid_dn)
        self.assertTrue(res)

    def test_fail(self):
        """Checking if incorrect DN will return False"""
        cert_file = open('fail.crt', 'r')
        cert_buffer = cert_file.read()
        valid_dn = getValidDNs_from_file()
        res = valid_cert(cert_buffer, valid_dn)
        self.assertFalse(res)



if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerExtractDN)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerTransformDNComponentsToStr))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerGetValidDNsFromFile))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerValidCert))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
