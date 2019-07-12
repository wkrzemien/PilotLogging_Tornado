import pika
# pylint: disable = invalid-name

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
channel.queue_declare(queue='test', durable=True)
channel.basic_consume(queue='test',
                      auto_ack=True,
                      on_message_callback=callback)

print "Start of receiving"
channel.start_consuming()

