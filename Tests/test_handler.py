""" Unit tests for handler
"""

# pylint: disable=line-too-long

import datetime
import unittest
import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from OpenSSL import crypto
from handler import extract_DN, getValidDNs_from_file, valid_cert, transform_dn_components_to_str, transform_str_to_dict, are_params_valid
from py_cert import create_CA, create_test_cert

@unittest.skip('Rewriting according to new changes')
class TestHandlerAreParamsValid(unittest.TestCase):
    """Unit tests for are_params_valid function"""
    ca_path = 'CA.crt'
    ca_key = 'CA.key'
    valid_test_cert = 'valid_test.crt'
    valid_test_key = 'valid_test.key'
    invalid_test_cert = 'invalid_test.crt'
    invalid_test_key = 'invalid_test.key'
    ca_subj_dict = {'Country':u'PL', 'State':u'Maze', 'Locality':u'KR', 
                    'Organization':u'test', 'OU':u'unittest', 'CN':u'CA'}
    valid_subj_dict = {'Country':u'PL', 'State':u'Maze', 'Locality':u'KR', 
                       'Organization':u'test', 'OU':u'unittest', 'CN':u'valid'}
    invalid_subj_dict = {'Country':u'PL', 'State':u'Maze', 'Locality':u'KR', 
                         'Organization':u'test', 'OU':u'unittest', 'CN':u'invalid'}
    network = {'Tornado':('127.0.0.1', 1027)}
    def setUp(self):
        """Create test files"""
        test_0 = open('test_0', 'w+')
        test_1 = open('test_1', 'w+')
        """Create test certs"""
        invalid_date = datetime.datetime.now()-datetime.timedelta(days=10)
        invalid_timedelta = datetime.timedelta(days=5)
        private_key_CA, CA_subject, CA_cert = create_CA(self.ca_path, self.ca_key, self.ca_subj_dict)
        create_test_cert(self.valid_test_cert, self.valid_test_key, private_key_CA, self.ca_subj_dict, self.valid_subj_dict)
        create_test_cert(path=self.invalid_test_cert, path_key=self.invalid_test_key, private_key_CA=private_key_CA, 
                         CA_subject=self.ca_subj_dict, test_subj_dict=self.invalid_subj_dict,
                         time_begin=invalid_date, time_delta=invalid_timedelta)

    def tearDown(self):
        """Remove testing files"""
        os.remove('test_0')
        os.remove('test_1')
        os.remove(self.ca_path)
        os.remove(self.ca_key)
    def test_success(self):
        """Check for test files"""
        files_to_check = ['test_0', 'test_1', self.ca_key, self.ca_path, self.valid_test_cert]
        self.assertTrue(are_params_valid(files_to_check, self.valid_test_cert, self.ca_path, self.network))
    def test_raising_correct_error(self):
        pass
        """Check if function raises IOError for invalid file name\n"""
#        files_to_check = ['test_0', 'test_unexpected']
#        self.assertRaisesRegexp(IOError, 'This test_unexpected cannot be accessed', are_params_valid, files_to_check )

class TestHandlerTransformDNComponentsToStr(unittest.TestCase):
    """ Unit tests for transform_dn_components_to_str
    """
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_success_possible_cert(self):
        """Success test for posible DN"""
        tested_dn = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        result_str = transform_dn_components_to_str(tested_dn)
        self.assertEqual(result_str, '/DC=ch/DC=cern/OU=computers/CN=lhcbi-cernvm03.cern.ch')
    def test_success_test_cert(self):
        """Success test for certificate, which is used in tests"""
        tested_cert_file = open('../testCerts/user.crt', 'r')
        tested_cert_data = tested_cert_file.read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, tested_cert_data)
        tested_dn =  transform_dn_components_to_str(cert.get_subject().get_components())
        self.assertEqual(tested_dn, '/C=PL/ST=User/L=KR/O=LocalFAke/CN=userCert/emailAddress=user@fake.pl')
    def test_raise_error_incorrect_dn(self):
        """If DN is incorrect this function must raise an ValueError"""
        tested_dn = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers', 'Ooops'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        self.assertRaises(ValueError, transform_dn_components_to_str, tested_dn)

class TestHandlerTransformStrToDict(unittest.TestCase):
    """ Unit tests for transform_str_to_dict
    """
    def test_success_possible_cert(self):
        """Success test for posible DN string"""
        tested_str = '/DC=ch/DC=cern/OU=computers/CN=lhcbi-cernvm03.cern.ch'
        result_dict = transform_str_to_dict(tested_str)
        self.assertEqual(result_dict, {'subject': ['DC', 'ch', 'DC', 'cern', 'OU', 'computers','CN', 'lhcbi-cernvm03.cern.ch']})



class TestHandlerExtractDN(unittest.TestCase):
    """Tests for extract_DN function"""
    ca_file_path = 'CA.crt'
    ca_key_path = 'CA.key'
    ca_subj_dict = {'Country':u'PL', 'State':u'Maze', 'Locality':u'KR', 'Organization':u'test', 'OU':u'unittest', 'CN':u'CA'}
    def setUp(self):
        """Creating test certificates for this tests"""
        create_CA(self.ca_file_path, self.ca_key_path, self.ca_subj_dict, serialization.Encoding.DER)
    def tearDown(self):
        """Remove certificates"""
        os.remove(self.ca_file_path)
        os.remove(self.ca_key_path)
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
        self.assertRaises(IOError, getValidDNs_from_file, 'it_does_not_exist.json')
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerTransformStrToDict))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerAreParamsValid))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerTransformDNComponentsToStr))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerGetValidDNsFromFile))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerValidCert))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
