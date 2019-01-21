#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is second try"""
import ssl
import json
import tornado.web
import tornado.httpserver
import tornado.ioloop
from stompSender import StompSender



def cert_to_dict(cert):
  '''Transform  SSL certificate DN to dictionary'''
  cert_dict = {}
  for i in range(len(cert['subject'])):
    cert_dict.update(dict(cert['subject'][i]))
  return cert_dict


def valid_cert(client_cert, validDNs):
  '''Comparing client DN in dictionary form to DN which are in text file'''
  client_dn = cert_to_dict(client_cert)
  return client_dn in validDNs


def getValidDNs(filename='Test_DN.json'):
  dnList = []
  with open(filename, "r") as fileDN:
    dnList = json.load(fileDN)
  return dnList

# pylint: disable = W0223, invalid-name, arguments-differ


class MainHandler(tornado.web.RequestHandler):
  """Request handler for json messages"""
  def __init__(self, *args, **kwargs):    # in args, kwargs, there will be all parameters you don't care, but needed for baseClass
    super(MainHandler, self).__init__(*args, **kwargs)
    self.sender =  StompSender({})

  def initialize(self):
    """Auth by cert"""
    self.current_DNs = getValidDNs()
    client_cert = self.request.get_ssl_certificate()
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
    print "sending message:" + str(message)
    self.sendMessage(msg)  # send message to MQ

  def sendMessage(self, message):
    # Just for a moment
    self.sender.sendMessage(message, flag='info')


class TestHandler(tornado.web.RequestHandler):
  """Request handler for the main page of the app localhost:1027"""

  def get(self):
    """Information about server which returns with  HTTP Get"""
    self.render("MainPage.html")

  def post(self):
    """Post function"""
    if self.get_argument('User') == "U" and self.get_argument('Password') == "R":
      self.write("Ok")
      self.redirect("https://localhost:1027/random")
    else:
      self.write("Nope")


def make_app():
  """Make app with two pages main and random"""
  return tornado.web.Application([(r"/", TestHandler),
                                  (r"/json", MainHandler)])


def generate_ssl_context():
  certDir = '../testCerts/'
  mySSLContex = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  mySSLContex.load_cert_chain(certDir+'server.crt', certDir+'server.key')
  mySSLContex.load_verify_locations(certDir+'CAcert.pem')
  mySSLContex.load_verify_locations(certDir+'user.crt')
  mySSLContex.verify_mode = ssl.CERT_REQUIRED
  return mySSLContex


if __name__ == "__main__":
  print "STARTING TORNADO SERVER!"
  app = make_app()
  ssl_ctx = generate_ssl_context()
  http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
  http_server.listen(1027)
  tornado.ioloop.IOLoop.current().start()
