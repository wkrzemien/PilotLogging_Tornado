#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This is second try"""
import ssl
import json
import tornado.web
import tornado.httpserver
import tornado.ioloop

print "here1"
certDir = '../testCerts/'
ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_ctx.load_cert_chain(certDir+'server.crt', certDir+'server.key')
ssl_ctx.load_verify_locations(certDir+'CAcert.pem')
ssl_ctx.load_verify_locations(certDir+'user.crt')
print "here2?"
# ssl_ctx.load_cert_chain("CA_test/localhost.cert.pem", "CA_test/localhost.key.pem")
# ssl_ctx.load_verify_locations("CA_test/ca.cert.pem")
# ssl_ctx.load_verify_locations("test/ca_client.cert.pem")
ssl_ctx.verify_mode = ssl.CERT_REQUIRED

def cert_to_dict(cert):
    '''Transform  SSL certificate DN to dictionary'''
    cert_dict = {}
    for i in range(len(cert['subject'])):
        cert_dict.update(dict(cert['subject'][i]))
    return cert_dict

def DN_check(filename, client_DN):
    '''Comparing client DN in dictionary form to DN which are in text file'''

    print "HERERE5!!"
    DN_file = open(filename, "r")
    cert_dictionary_list = []
    for line in DN_file:
        dictionary = json.loads(line)
        cert_dictionary_list.append(dictionary)
    list_of_equal = filter(lambda x: x == client_DN, cert_dictionary_list)
    if list_of_equal != 0:
        return True
        
# pylint: disable = W0223, invalid-name, arguments-differ

class MainHandler(tornado.web.RequestHandler):
    """Request handler for the main page of the app localhost:1027"""
    def get(self):
        """Information about server which returns with  HTTP Get"""
        print "HERERE4!!"
        self.render("MainPage.html")
    def post(self):
        """Post function"""
        print "HERERE3!!"
        if self.get_argument('User') == "U" and self.get_argument('Password') == "R":
            self.write("Ok")
            self.redirect("https://localhost:1027/random")
        else:
            self.write("Nope")

class JsonHandler(tornado.web.RequestHandler):
    """Request handler for json messages"""
    def initialize(self):
        print "HERERE!!"
        """Auth by cert"""
        client_cert = self.request.get_ssl_certificate()
        self.client_dn = cert_to_dict(client_cert)
        print "here"
        if not DN_check("Test_DN", self.client_dn):
            self.finish()
    def get(self):
        """get function of jsonhandler"""
        print "HERERE100!!"
        self.write(self.client_dn)
    def post(self):
        """post function of json handler"""
        print "HERERE2!!"
        self.write(self.request.get_ssl_certificate())
        json_message = json.loads(self.request.body.decode('string-escape').strip('"'))
        #json.loads(json.loads(self.request.body)) #you can try with this too ^^
        if json_message["source"] == "InstallDIRAC":
            self.write("\nSource is correct")
def make_app():
    """Make app with two pages main and random"""
    return tornado.web.Application([(r"/", MainHandler),
                                    (r"/json", JsonHandler)])

if __name__ == "__main__":
    print "STARTING"
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
    http_server.listen(1027)
    tornado.ioloop.IOLoop.current().start()
