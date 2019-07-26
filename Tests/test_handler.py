""" Unit tests for handler
"""

# pylint: disable=line-too-long

import unittest
import os
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
        tested_dn = extract_DN(tested_cert_data)
        self.assertEqual(tested_dn, '/C=PL/ST=User/L=KR/O=LocalFAke/CN=userCert/emailAddress=user@fake.pl')
    def test_raise_error_incorrect_dn(self):
        """If DN is incorrect this function must raise an ValueError"""
        tested_dn = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers', 'Ooops'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        self.assertRaises(ValueError, transformDNComponentsToStr, tested_dn)




@unittest.skip("We need to rewrite this part according to new functions in handler")
class TestHandlerExtractDN(unittest.TestCase):
    """Tests for extract_DN function"""
    def setUp(self):
        """Creating test certificates for this tests"""
        ca_file_path = 'CA.crt'
        ca_key_path = 'CA.key'
        ca_subj_dict = {'Country':u'PL', 'State':u'Maze', 'Locality':u'KR', 'Organization':u'test', 'OU':u'unittest', 'CN':u'CA'}
        create_CA(ca_file_path, ca_key_path, ca_subj_dict)
    def tearDown(self):
        """Remove certificates"""
        os.remove('CA.crt')
        os.remove('CA.key')
    def test_success(self):
        """Check if extract dn works on created in setUp certificate""" 
        pass
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

@unittest.skip("We need to rewrite this part according to new functions in handler")
class TestHandlerValidCert(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_success(self):
        cert = {'issuer': ((('countryName', 'IL'),),
                           (('organizationName', 'StartCom Ltd.'),),
                           (('organizationalUnitName',
                             'Secure Digital Certificate Signing'),),
                           (('commonName',
                             'StartCom Class 2 Primary Intermediate Server CA'),)),
                'notAfter': 'Nov 22 08:15:19 2013 GMT',
                'notBefore': 'Nov 21 03:09:52 2011 GMT',
                'serialNumber': '95F0',
                'subject': ((('countryName', 'PL'),),
                            (('stateOrProvinceName', 'MAZOWIECKIE'),),
                            (('localityName', 'Krakow'),),
                            (('organizationName', 'Some_organization'),),
                            (('organizationalUnitName', 'Unit'),)
                           ),
                'version': 3}
        valid_dn = getValidDNs_from_file()
        res = valid_cert(cert, valid_dn)
        self.assertTrue(res)

    def test_fail(self):
        cert = {'issuer': ((('countryName', 'IL'),),
                           (('organizationName', 'StartCom Ltd.'),),
                           (('organizationalUnitName',
                             'Secure Digital Certificate Signing'),),
                           (('commonName',
                             'StartCom Class 2 Primary Intermediate Server CA'),)),
                'notAfter': 'Nov 22 08:15:19 2013 GMT',
                'notBefore': 'Nov 21 03:09:52 2011 GMT',
                'serialNumber': '95F0',
                'subject': ((('description', '571208-SLe257oHY9fVQ07Z'),),
                            (('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'San Francisco'),),
                            (('organizationName', 'Electronic Frontier Foundation, Inc.'),),
                            (('commonName', '*.eff.org'),),
                            (('emailAddress', 'hostmaster@eff.org'),)),
                'subjectAltName': (('DNS', '*.eff.org'), ('DNS', 'eff.org')),
                'version': 3}
        valid_dn = getValidDNs_from_file()
        res = valid_cert(cert, valid_dn)
        self.assertFalse(res)



if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerExtractDN)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerTransformDNComponentsToStr))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerGetValidDNsFromFile))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestHandlerValidCert))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
