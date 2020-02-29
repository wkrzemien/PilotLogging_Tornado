''' Creating and signing certificates via Python'''
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID



# pylint: disable = W0223, invalid-name, arguments-differ, line-too-long
def create_CA(path, path_key, CA_subj_dict, serialization_format=serialization.Encoding.PEM, 
              time_begin=datetime.datetime.now(), time_delta=datetime.timedelta(days=10)):
    '''Creating CA
       dirpath - path to directory, where CA will be placed
       CA_subj_dict - dict, like this CA_subj_dict={'Country':u'PL', ...}'''
    private_key_CA = rsa.generate_private_key(public_exponent=65537, key_size=2048,
                                              backend=default_backend())
    public_key_CA = private_key_CA.public_key()
    with open(path_key, 'wb') as f:
        f.write(private_key_CA.private_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PrivateFormat.TraditionalOpenSSL,
                                             encryption_algorithm=serialization.BestAvailableEncryption(b"password")))

    CA_subject = [x509.NameAttribute(NameOID.COUNTRY_NAME, CA_subj_dict['Country']),
                  x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, CA_subj_dict['State']),
                  x509.NameAttribute(NameOID.LOCALITY_NAME, CA_subj_dict['Locality']),
                  x509.NameAttribute(NameOID.ORGANIZATION_NAME, CA_subj_dict['Organization']),
                  x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, CA_subj_dict['OU']),
                  x509.NameAttribute(NameOID.COMMON_NAME, CA_subj_dict['CN'])]

    CA_cert = x509.CertificateBuilder().subject_name(x509.Name(CA_subject))
    CA_cert = CA_cert.issuer_name(x509.Name(CA_subject))
    CA_cert = CA_cert.public_key(public_key_CA)
    CA_cert = CA_cert.serial_number(x509.random_serial_number())
    CA_cert = CA_cert.not_valid_before(time_begin)
    CA_cert = CA_cert.not_valid_after(datetime.datetime.utcnow()+time_delta)
    CA_cert = CA_cert.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    CA_cert = CA_cert.sign(private_key_CA, hashes.SHA256(), default_backend())
    with open(path, 'wb') as CAcert:
        CAcert.write(CA_cert.public_bytes(serialization_format))
    return private_key_CA, CA_subject, CA_cert

def create_test_cert(path, path_key, private_key_CA, CA_subject, test_subj_dict,
                     serialization_format=serialization.Encoding.PEM, time_begin=datetime.datetime.now(), 
                     time_delta=datetime.timedelta(days=10)):
    '''Creating test cert
       test_subj_dict = {'Country':u'UK', etc}'''
    Test_subject = [x509.NameAttribute(NameOID.COUNTRY_NAME, test_subj_dict['Country']),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, test_subj_dict['State']),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, test_subj_dict['Locality']),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, test_subj_dict['Organization']),
                    x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, test_subj_dict['OU']),
                    x509.NameAttribute(NameOID.COMMON_NAME, test_subj_dict['CN'])]
    private_test_key = rsa.generate_private_key(public_exponent=65537, key_size=2048,
                                                backend=default_backend())
    public_test_key = private_test_key.public_key()
    test_cert = x509.CertificateBuilder().subject_name(x509.Name(Test_subject))
    test_cert = test_cert.issuer_name(x509.Name(CA_subject))
    test_cert = test_cert.public_key(public_test_key)
    test_cert = test_cert.serial_number(x509.random_serial_number())
    test_cert = test_cert.not_valid_before(time_begin)
    test_cert = test_cert.not_valid_after(time_begin+time_delta)
    test_cert = test_cert.sign(private_key_CA, hashes.SHA256(), default_backend())
    with open(path_key, 'wb') as f:
        f.write(private_test_key.private_bytes(encoding=serialization.Encoding.PEM,
                                               format=serialization.PrivateFormat.TraditionalOpenSSL,
                                               encryption_algorithm=serialization.BestAvailableEncryption(b"test")))
    with open(path, 'wb') as TestCert:
        TestCert.write(test_cert.public_bytes(serialization_format))
    return private_test_key, test_cert


if  __name__ == '__main__':
    CA_subj = {'Country':u'PL', 'State':u'Mazowieckie', 'Locality':u'Warszawa',
               'Organization':u'NCBJ', 'OU':u'Student', 'CN':u'CA'}
    test_subj = {'Country':u'PL', 'State':u'Mazowieckie', 'Locality':u'Warszawa',
                 'Organization':u'NCBJ', 'OU':u'Student', 'CN':u'test'}
    key_CA, CA_subj, CA_crt = create_CA('tc/CAcert.pem', 'tc/CAkey.pem', CA_subj)
    test_key, test_crt = create_test_cert('tc/user.crt', 'tc/user.key', key_CA, CA_subj, test_subj)
