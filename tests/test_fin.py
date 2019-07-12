"""This is test for the json handler"""
import os
import json
import requests
import pika
# pylint: disable = invalid-name


certDir = '../testCerts/'
client_cert = os.path.join(certDir+'user.crt')
client_key = os.path.join(certDir+'user.key')
CAcert = os.path.join(certDir+'CAcert.pem')

URL = 'https://localhost:1027'
msg = {
  'status': 'info',
  'phase': 'Installing',
  'timestamp': '1427121370.7',
  'messageContent': 'Uname = Linux localhost 3.10.64-85.cernvm.x86_64',
  'pilotUUID': 'eda78924-d169-11e4-bfd2-0800275d1a0a',
  'source': 'InstallDIRAC'
}

json_msg = json.dumps(msg, separators=(', ', ': '))

r2 = requests.post(URL, cert=(client_cert, client_key),
                   verify=CAcert, json=json_msg)
print r2.text
