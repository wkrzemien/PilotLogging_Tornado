"""This module read config file and checks if certificates are ok """

import json
from OpenSSL import crypto


class ConfigError(Exception):
    """Error in configuration"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def verify(CA, cert):
    """This functions checks two certificates,
       which are OpenSSL.crypto.X509 variables
    """
    store = crypto.X509Store()
    store.add_cert(CA)
    store_context = crypto.X509StoreContext(store, cert)
    if store_context.verify_certificate() is None:
        return True
    else:
        return False

try:
    with open('handler_config.json', 'r') as config_file:
        config_json = json.load(config_file)
    
        Tornado_host = config_json['Tornado_host']
        server_cert_file = open(config_json['server_cert'])
        CA_cert_file = open(config_json['CA_cert'])
    
        server_cert_data = server_cert_file.read()
        CA_cert_data = CA_cert_file.read()
    
        server_cert = crypto.load_certificate(crypto.FILETYPE_PEM, server_cert_data)
        CA_cert = crypto.load_certificate(crypto.FILETYPE_PEM, CA_cert_data)
    
        server_DN_crypto = server_cert.get_subject()
        server_DN = dict(server_DN_crypto.get_components())
    
        if server_DN['CN'] != Tornado_host:
            raise ConfigError('Hostname doesn`t match certificates CN')
        else:
            print 'hostname is ok'
    
        if verify(CA_cert, server_cert):
            print 'certificate is ok'
        else:
            raise ConfigError('Certificate isn`t signed by provided CA')
except IOError:
    print 'I can`t find config file, please check it'
    
