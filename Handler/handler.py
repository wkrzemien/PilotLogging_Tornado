#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is second try"""
import ssl
import json
import tornado.web
import tornado.httpserver
import tornado.ioloop


def cert_to_dict(cert):
  '''Transform  SSL certificate DN to dictionary'''
  cert_dict = {}
  for i in range(len(cert['subject'])):
    cert_dict.update(dict(cert['subject'][i]))
  return cert_dict


def valid_cert(client_cert, validDNs):
  '''Comparing client DN in dictionary form to DN which are in text file'''
  client_dn = cert_to_dict(client_cert)
  print client_dn
  return client_dn in validDNs


def getValidDNs(filename='Test_DN'):
  dnList = []
  with open(filename, "r") as fileDN:
    dnList = json.load(fileDN)
  return dnList

# pylint: disable = W0223, invalid-name, arguments-differ


class MainHandler(tornado.web.RequestHandler):
  """Request handler for json messages"""

  def initialize(self):
    """Auth by cert"""
    self.current_DNs = getValidDNs()
    client_cert = self.request.get_ssl_certificate()
    if not valid_cert(client_cert, validDNs=self.current_DNs):
      print "This certificate is not authorized!"
      self.finish()

  def get(self):
    """get function of jsonhandler"""
    self.write("blabla")

  def post(self):
    """post function of json handler"""
    self.write(self.request.get_ssl_certificate())
    message = json.loads(
        self.request.body.decode('string-escape').strip('"'))
    self.sendMessage(message)  # send message to MQ

  def sendMessage(self, message):
    # Just for a moment
    if message["source"] == "InstallDIRAC":
      self.write("\nSource is correct")


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
  ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  ssl_ctx.load_cert_chain(certDir+'server.crt', certDir+'server.key')
  ssl_ctx.load_verify_locations(certDir+'CAcert.pem')
  ssl_ctx.load_verify_locations(certDir+'user.crt')
  ssl_ctx.verify_mode = ssl.CERT_REQUIRED
  return ssl_ctx


if __name__ == "__main__":
  print "STARTING TORNADO SERVER!"
  app = make_app()
  ssl_ctx = generate_ssl_context()
  http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
  http_server.listen(1027)
  tornado.ioloop.IOLoop.current().start()
