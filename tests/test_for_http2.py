"""This is test for the json handler"""
import json
import requests
import os
import tornado.httpclient
# pylint: disable = invalid-name
certDir = '../testCerts/'
localcert = os.path.join(certDir+'server.crt')
localkey = os.path.join(certDir+'server.key')
CAcert = os.path.join(certDir+'CAcert.pem')

client_cert = os.path.join(certDir+'user.crt')
client_key = os.path.join(certDir+'user.key')

# localcert = os.path.join("CA_test/localhost.cert.pem")
# localkey = os.path.join("CA_test/localhost.key.pem")
# CAcert = os.path.join("CA_test/ca.cert.pem")

# client_cert = os.path.join("test/test_client.cert.pem")
# client_key = os.path.join("test/test_client.key.pem")

# another_client_cert = os.path.join("CA_test/test.cert.pem")
# another_client_key = os.path.join("CA_test/test.key.pem")
msg = {
    'status': 'info',
    'phase': 'Installing',
    'timestamp': '1427121370.7',
    'messageContent': 'Uname = Linux localhost 3.10.64-85.cernvm.x86_64',
    'pilotUUID': 'eda78924-d169-11e4-bfd2-0800275d1a0a',
    'source': 'InstallDIRAC'
    }

URL = 'https://localhost:1027/json'
Json_msg = json.dumps(msg, separators=(', ', ': '))
P = requests.get(URL, cert=(client_cert, client_key), verify=CAcert)
# P = requests.get(URL, cert=(client_cert, client_key), verify=False)

print P.text
'''
Client = tornado.httpclient.HTTPClient()
Request = tornado.httpclient.HTTPRequest(URL, method='GET', ca_certs="CA_test/ca.cert.pem", client_key="test/test_client.key.pem", client_cert="test/test_client.cert.pem")
Responce = Client.fetch(Request) 
print(Responce.body)
Client.close()
'''
