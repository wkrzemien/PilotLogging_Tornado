""" Unit tests for handler
"""

# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
from handler import extract_DN, getValidDNs_from_file, valid_cert, transformDNComponentsToStr
from OpenSSL import crypto

class Testhandler_transformDNComponentsToStr(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_success_possible_cert(self):
        tested_DN = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        result_str = transformDNComponentsToStr(tested_DN)
        self.assertEqual(result_str, '/DC=ch/DC=cern/OU=computers/CN=lhcbi-cernvm03.cern.ch')
    def test_success_test_cert(self):
        tested_cert_file = open('../testCerts/user.crt', 'r')
        tested_cert_data = tested_cert_file.read() 
        tested_DN = extract_DN(tested_cert_data)
        self.assertEqual(tested_DN, '/C=PL/ST=User/L=KR/O=LocalFAke/CN=userCert/emailAddress=user@fake.pl')
    def test_raise_Error_incorrect_DN(self):
        tested_DN = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'computers', 'Ooops'), ('CN', 'lhcbi-cernvm03.cern.ch')]
        self.assertRaises(ValueError, transformDNComponentsToStr, tested_DN)




@unittest.skip("We need to rewrite this part according to new functions in handler")
class Testhandler_extract_DN(unittest.TestCase):
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
                'subject': ((('description', '571208-SLe257oHY9fVQ07Z'),),
                            (('countryName', 'US'),),
                            (('stateOrProvinceName', 'California'),),
                            (('localityName', 'San Francisco'),),
                            (('organizationName', 'Electronic Frontier Foundation, Inc.'),),
                            (('commonName', '*.eff.org'),),
                            (('emailAddress', 'hostmaster@eff.org'),)),
                'subjectAltName': (('DNS', '*.eff.org'), ('DNS', 'eff.org')),
                'version': 3}
        test_subject = cert['subject']
        for a in test_subject:
            key, value = a[0][0], a[0][1]
            self.assertEqual(value, extract_DN(cert)[key])
# class Testhandler_getValidDNs_from_file(unittest.TestCase):
    # def setUp(self):
        # pass

    # def tearDown(self):
        # pass

    # def test_success(self):
        # res = getValidDNs_from_file()
        # self.assertTrue(res)

    # def test_fail(self):
        # res = getValidDNs_from_file(filename='it_does_not_exist')
        # self.assertFalse(res)

# class Testhandler_valid_cert(unittest.TestCase):
    # def setUp(self):
        # pass
    # def tearDown(self):
        # pass
    # def test_success(self):
        # cert = {'issuer': ((('countryName', 'IL'),),
                           # (('organizationName', 'StartCom Ltd.'),),
                           # (('organizationalUnitName',
                             # 'Secure Digital Certificate Signing'),),
                           # (('commonName',
                             # 'StartCom Class 2 Primary Intermediate Server CA'),)),
                # 'notAfter': 'Nov 22 08:15:19 2013 GMT',
                # 'notBefore': 'Nov 21 03:09:52 2011 GMT',
                # 'serialNumber': '95F0',
                # 'subject': ((('countryName', 'PL'),),
                            # (('stateOrProvinceName', 'MAZOWIECKIE'),),
                            # (('localityName', 'Krakow'),),
                            # (('organizationName', 'Some_organization'),),
                            # (('organizationalUnitName', 'Unit'),)
                           # ),
                # 'version': 3}
        # valid_DN = getValidDNs_from_file()
        # res = valid_cert(cert, valid_DN)
        # self.assertTrue(res)

    # def test_fail(self):
        # cert = {'issuer': ((('countryName', 'IL'),),
                           # (('organizationName', 'StartCom Ltd.'),),
                           # (('organizationalUnitName',
                             # 'Secure Digital Certificate Signing'),),
                           # (('commonName',
                             # 'StartCom Class 2 Primary Intermediate Server CA'),)),
                # 'notAfter': 'Nov 22 08:15:19 2013 GMT',
                # 'notBefore': 'Nov 21 03:09:52 2011 GMT',
                # 'serialNumber': '95F0',
                # 'subject': ((('description', '571208-SLe257oHY9fVQ07Z'),),
                            # (('countryName', 'US'),),
                            # (('stateOrProvinceName', 'California'),),
                            # (('localityName', 'San Francisco'),),
                            # (('organizationName', 'Electronic Frontier Foundation, Inc.'),),
                            # (('commonName', '*.eff.org'),),
                            # (('emailAddress', 'hostmaster@eff.org'),)),
                # 'subjectAltName': (('DNS', '*.eff.org'), ('DNS', 'eff.org')),
                # 'version': 3}
        # valid_DN = getValidDNs_from_file()
        # res = valid_cert(cert, valid_DN)
        # self.assertFalse(res)



if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_extract_DN)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_transformDNComponentsToStr))
    # suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_getValidDNs_from_file))
    # suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_valid_cert))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
