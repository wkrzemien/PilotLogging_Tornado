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
receiver_host='localhost'

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

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=receiver_host, port=5672))
channel = connection.channel()
channel.queue_declare(queue='test', durable=True)
channel.basic_consume(queue='test',
                      auto_ack=True,
                      on_message_callback=callback)

print "Start of receiving"
channel.start_consuming()
