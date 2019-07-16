"""This module describes Tornado handler,
   which receives a message from certified sender,'
   checks certificate and certficate_DN
   and if all is ok send message to message queue,
   configuration is described in handler_config.json"""
import sys
import ssl
import json
import requests
import tornado.web
import tornado.httpserver
import tornado.ioloop
from OpenSSL import crypto
from stompSender import StompSender


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


def extract_DN(cert):
    '''Extract  SSL certificate DN to dictionary
       cert - dictionary, which is returned by ssl.getpeercert()'''
    cert_dict = {}
    for i in range(len(cert['subject'])):
        cert_dict.update(dict(cert['subject'][i]))
    return cert_dict


def valid_cert(client_cert, validDNs):
    '''Comparing client DN in dictionary form to DN which are in text file'''
    client_dn = extract_DN(client_cert)
    return client_dn in validDNs

def loadMQConfig(filename='handler_config.json'):
    """This function loads configuration for MQ from json file"""
    conf = {}
    try:
        with open(filename) as myFile:
            conf = json.load(myFile)
    except IOError:
        pass
    return conf

def getValidDNs_from_file(filename='Test_DN.json'):
    """This function create list of valid dn from json file"""
    dn_list = []
    try:
        with open(filename) as fileDN:
            dn_list = json.load(fileDN)
    except IOError:
        pass
    return dn_list

def getValidDNs_from_url(url):
    """This function create list of valid dn from url"""
    request = requests.get(url, verify=False)
    pilot_list = request.json()
    dn_list = pilot_list['DNs'].values()
    return dn_list
  # pylint: disable = W0223, invalid-name, arguments-differ

class MainHandler(tornado.web.RequestHandler):
    """Request handler for json messages"""
    def __init__(self, *args, **kwargs):# in args, kwargs, there will be all parameters you don't care, but needed for baseClass
        super(MainHandler, self).__init__(*args, **kwargs)
        conf = loadMQConfig()
        self.sender = StompSender(conf)
    def initialize(self):
        """Auth by cert"""
        self.current_DNs = getValidDNs_from_file()
        client_cert = self.request.get_ssl_certificate()# return dict
        if not valid_cert(client_cert, validDNs=self.current_DNs):
            print "This certificate is not authorized!"
            self.finish()
    def get(self):
        """get function of jsonhandler"""
        self.write("getting some info")
    def post(self):
        """post function of json handler"""
        self.write(self.request.get_ssl_certificate())
        msg = self.request.body.decode('string-escape').strip('"')
        message = json.loads(msg)
        self.sendMessage(msg)
    def sendMessage(self, message):
        """This method sends message to mq"""
        print "sending message:" + str(message)
        self.sender.sendMessage(message)
def make_app():
    """Make app with page"""
    return tornado.web.Application([(r"/", MainHandler)])

def generate_ssl_context(server_certificate, server_key, ca_cert):
    """This function generates an ssl context for Tornado handler"""
    mySSLContex = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    mySSLContex.load_cert_chain(server_certificate, server_key)
    mySSLContex.load_verify_locations(ca_cert)
    mySSLContex.verify_mode = ssl.CERT_REQUIRED
    return mySSLContex
if __name__ == "__main__":

    #define("host", default="localhost", help="app host", type=str)
    #define("port", default=8888, help="app port", type=int)
    #define("certPath", default="../testCerts/", help="path to certificates", type=str)
    #options.parse_command_line()

    ##todo it must be taken from some config file
    #server_cert = options.certPath + 'test.crt'
    #server_key = options.certPath + 'test.key'
    #ca_cert = options.certPath +'CAcert.pem'

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

    print "STARTING TORNADO SERVER! Host:%s, Port:%i"%(config_json['Tornado_host'], config_json['Tornado_port'])

    app = make_app()
    ssl_ctx = generate_ssl_context(config_json['server_cert'], config_json['server_key'], config_json['CA_cert'])
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
    http_server.listen(config_json['Tornado_port'])
    tornado.ioloop.IOLoop.current().start()
