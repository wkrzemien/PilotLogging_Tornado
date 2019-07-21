"""This module describes Tornado handler,
   which receives a message from certified sender,'
   checks certificate and certficate_DN
   and if all is ok send message to message queue,
   configuration is described in handler_config.json"""
import ssl
import json
import requests
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import options, define
# from OpenSSL import crypto
from stompSender import StompSender

class ConfigError(Exception):
    """Error in configuration"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


# def verify(ca, cert):
    # """This functions checks two certificates,
       # which are OpenSSL.crypto.X509 variables
    # """
    # store = crypto.X509Store()
    # store.add_cert(ca)
    # store_context = crypto.X509StoreContext(store, cert)
    # return True if store_context.verify_certificate() is None else False


def readConfigFile(configuration_file):
    """Read config file and return dict of params"""
    try:
        with open(configuration_file, 'r') as config_file:
            params = json.load(config_file)
            return params
    except IOError:
        raise IOError('I can`t find config file, please check it')

def areParamsValid(config_json):
    """Check if cert from params was signed by CA
       and if hostname from params matches cert`s CN"""
    app_host = config_json['host']
    server_cert_file = open(config_json['server_cert'])
    CA_cert_file = open(config_json['ca_cert'])
    server_cert_data = server_cert_file.read()
    CA_cert_data = CA_cert_file.read()
    # server_cert = crypto.load_certificate(crypto.FILETYPE_PEM, server_cert_data)
    # CA_cert = crypto.load_certificate(crypto.FILETYPE_PEM, CA_cert_data)
    # server_DN_crypto = server_cert.get_subject()
    # server_DN = dict(server_DN_crypto.get_components())
    # if server_DN['CN'] != app_host:
        # print 'Hostname:'
        # print app_host
        # print 'Certificate CN:'
        # print server_DN['CN']
        # raise ConfigError('Hostname doesn`t match certificates CN')
    # elif verify(CA_cert, server_cert) != True:
        # raise ConfigError('Certificate isn`t signed by provided CA')
    # else:
    return True



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
    print "client_dn %s"% str(client_dn)
    return client_dn in validDNs

def loadMQConfig(filename='handler_config.json'):
    """This function loads configuration for MQ from json file"""
    conf = {}
    try:
        with open(filename) as config_file:
            pre_conf = json.load(config_file)
            conf['Host'] = pre_conf['mq_host']
            conf['Port'] = pre_conf['mq_port']
            conf['QueuePath'] = pre_conf['mq_queue']
            conf['Username'] = pre_conf['mq_user']
            conf['Password'] = pre_conf['mq_password']
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
        # print "client_cert %s" %str(client_cert)
        # if not valid_cert(client_cert, validDNs=self.current_DNs):
            # print "This certificate is not authorized!"
            # self.finish()

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

    # params = readConfigFile('handler_config.json')


    define("host", default='localhost', help="tornado host", type=str)
    define("port", default=1027, help="tornado port", type=int)

    define("server_cert", default="../testCerts/server.crt", help="server certificate", type=str)
    define("server_key", default="../testCerts/server.key", help="server key", type=str)
    define("CA_cert", default="../testCerts/CAcert.pem", help="CA certificate", type=str)

    define("mq_host", default="127.0.0.1", help="MQ server host", type=str)
    define("mq_port", default=61613, help="MQ server port", type=int)
    define("mq_queuePath", default="/queue/test", help="MQ queue name", type=str)
    define("mq_username", default='guest', help="MQ username", type=str)
    define("mq_password", default='guest', help="MQ password", type=str)

    define("dn_filename", default='Test_DN.json', help="path to file with valid DNs", type=str)

    define("config", type=str, help="path to config file",
       callback=lambda path: options.parse_config_file(path, final=False))
    options.parse_command_line()

    # areParamsValid(options.as_dict())

    print "STARTING TORNADO SERVER! Host:%s, Port:%i"%(options.host, options.port)
    print (str(options.as_dict()))

    # app = make_app()
    # ssl_ctx = generate_ssl_context(options.server_cert, options.server_key, options.CA_cert)
    # http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
    # http_server.listen(options.port)
    # tornado.ioloop.IOLoop.current().start()
