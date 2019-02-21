'''Another way to create and sign certificates  via Python'''
from random import randint
from OpenSSL.crypto import PKey, TYPE_RSA, X509, X509Extension, dump_certificate, FILETYPE_PEM
from cryptography.hazmat.primitives import serialization
# pylint: disable = W0223, invalid-name, arguments-differ

key_CA = PKey()
key_CA.generate_key(TYPE_RSA, 2048)
CA=X509()
CA.set_serial_number(randint(0, 100))
CA_subject = {'C':'PL', 'ST':'Mazowieckie', 'L':'Warsaw', 'O':'CA', 'CN':'example.com'}
CA.get_subject().C = CA_subject['C']
CA.get_subject().ST = CA_subject['ST']
CA.get_subject().L = CA_subject['L']
CA.get_subject().O = CA_subject['O']
CA.get_subject().CN = CA_subject['CN']
CA.set_issuer(CA.get_subject())
CA.set_pubkey(key_CA)
CA.gmtime_adj_notBefore(0)
CA.gmtime_adj_notAfter(24*3600)
CA.add_extensions([X509Extension("basicConstraints", True,
                                 "CA:TRUE, pathlen:0"),])
CA.sign(key_CA, "sha1")

with open('tc/CA_secundo.pem', 'wb') as CAcert:
    CAcert.write(dump_certificate(FILETYPE_PEM, CA.to_cryptography()))

key_test = PKey()
key_test.generate_key(TYPE_RSA, 2048)
test=X509()
test.set_serial_number(randint(0, 100))
test_subject = {'C':'PL', 'ST':'Mazowieckie', 'L':'Warsaw', 'O':'test', 'CN':'localhost'}
test.get_subject().C = test_subject['C']
test.get_subject().ST = test_subject['ST']
test.get_subject().L = test_subject['L']
test.get_subject().O = test_subject['O']
test.get_subject().CN = test_subject['CN']
test.set_issuer(CA.get_subject())
test.set_pubkey(key_test)
test.gmtime_adj_notBefore(0)
test.gmtime_adj_notAfter(24*3600)
test.sign(key_CA, "sha1")
with open('tc/test_secundo.pem', 'wb') as test_cert:
    test_cert.write(dump_certificate(FILETYPE_PEM, test.to_cryptography()))
