""" Unit tests for handler
"""

# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
from handler import extract_DN, getValidDNs, valid_cert


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
class Testhandler_getValidDNs(unittest.TestCase):
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

class Testhandler_valid_cert(unittest.TestCase):
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
        valid_DN = getValidDNs_from_url()
        res = valid_cert(cert, valid_DN)
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
        valid_DN = getValidDNs()
        res = valid_cert(cert, valid_DN)
        self.assertFalse(res)



if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_extract_DN)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_getValidDNs))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Testhandler_valid_cert))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
