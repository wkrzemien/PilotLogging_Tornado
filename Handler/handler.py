# -*- coding: utf-8 -*-
import sys
import ssl
import json
import requests
import tornado.web
import tornado.httpserver
import tornado.ioloop
from stompSender import StompSender
from tornado.options import options, define


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

def loadMQConfig(filename='mq_config.json'):
  conf = {}
  try:
    with open(filename) as myFile:
      conf = json.load(myFile)
  except IOError:
    pass
  return conf

def getValidDNs_from_file(filename='Test_DN.json'):
  dnList = []
  try:
    with open(filename) as fileDN:
      dnList = json.load(fileDN)
  except IOError:
    pass
  return dnList

def getValidDNs_from_url(url):
  request = requests.get(url, verify=False)
  pilotList = request.json()
  dNlist = pilotList['DNs'].values()
  return dNlist
# pylint: disable = W0223, invalid-name, arguments-differ


class MainHandler(tornado.web.RequestHandler):
  """Request handler for json messages"""
  def __init__(self, *args, **kwargs):    # in args, kwargs, there will be all parameters you don't care, but needed for baseClass
    super(MainHandler, self).__init__(*args, **kwargs)
    conf = loadMQConfig()
    self.sender =  StompSender(conf)
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
    print "sending message:" + str(message)
    self.sender.sendMessage(message)
    print "fin"

def make_app():
  """Make app with page"""
  return tornado.web.Application([(r"/", MainHandler)])

def generate_ssl_context(certDir='../testCerts/'):
  mySSLContex = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  mySSLContex.load_cert_chain(certDir+'server.crt', certDir+'server.key')
  mySSLContex.load_verify_locations(certDir+'CAcert.pem')
  mySSLContex.load_verify_locations(certDir+'user.crt')
  mySSLContex.verify_mode = ssl.CERT_REQUIRED
  return mySSLContex

if __name__ == "__main__":
  define("host", default="localhost", help="app host", type=str)
  define("port", default=1027, help="app port", type=int)
  options.parse_command_line()
  print "STARTING TORNADO SERVER!"
  app = make_app()
  ssl_ctx = generate_ssl_context()
  http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.current().start()
